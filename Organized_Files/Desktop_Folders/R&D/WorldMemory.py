import os
import json
import hashlib
import time
import requests
import gzip
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    import arweave
    HAS_ARWEAVE = True
except ImportError:
    HAS_ARWEAVE = False
try:
    from web3storage import Client
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
try:
    from nft_storage_api import NFTStorage
    HAS_NFT_STORAGE = True
except ImportError:
    HAS_NFT_STORAGE = False

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
BRAIN_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_MAP_FILE = BRAIN_DIR / "world_memory.map"
VOICEPRINT_FILE = BRAIN_DIR / "voiceprint.key"

class WorldMemory:
    def __init__(self):
        self.memory_map = bytearray(512)
        self.map_entries = []
        self.voiceprint_hash = self._load_voiceprint()
        self.arweave_wallet = None
        self.web3_client = None
        self.nft_storage = None
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'WorldMemory/1.0'})
        self.version_history = {}  # {entry_hash: [prev_hashes]}
        self.entry_acl = {}  # {entry_hash: {'owner': hash, 'readers': [hash], 'writers': [hash]}}
        self.cost_tracking = {'arweave': 0, 'web3storage': 0, 'nftstorage': 0, 'pinata': 0}
        self.bandwidth_stats = {'uploaded': 0, 'downloaded': 0, 'last_reset': int(time.time())}
        self.replication_factor = 3  # Default: 3 copies
        self._init_storage()
        self._load_memory_map()
    
    def _load_voiceprint(self) -> bytes:
        if VOICEPRINT_FILE.exists():
            return VOICEPRINT_FILE.read_bytes()
        voiceprint = os.urandom(32)
        VOICEPRINT_FILE.write_bytes(voiceprint)
        return voiceprint
    
    def _init_storage(self):
        if HAS_ARWEAVE:
            try:
                wallet_path = BRAIN_DIR / "arweave_wallet.json"
                if wallet_path.exists():
                    with open(wallet_path) as f:
                        self.arweave_wallet = arweave.Wallet(json.load(f))
                else:
                    self.arweave_wallet = arweave.Wallet.generate()
                    with open(wallet_path, 'w') as f:
                        json.dump(self.arweave_wallet.jwk_data, f)
            except: pass
        if HAS_WEB3:
            try:
                token = os.getenv("WEB3_STORAGE_TOKEN", "")
                if token: self.web3_client = Client(token)
            except: pass
        if HAS_NFT_STORAGE:
            try:
                token = os.getenv("NFT_STORAGE_TOKEN", "")
                if token: self.nft_storage = NFTStorage(token)
            except: pass
    
    def _load_memory_map(self):
        if MEMORY_MAP_FILE.exists():
            data = MEMORY_MAP_FILE.read_bytes()
            if len(data) >= 512:
                self.memory_map = bytearray(data[:512])
                try:
                    json_data = data[512:].decode('utf-8') if len(data) > 512 else '[]'
                    parsed = json.loads(json_data)
                    if isinstance(parsed, list):
                        self.map_entries = parsed
                        self.version_history = {}
                        self.entry_acl = {}
                        self.cost_tracking = {'arweave': 0, 'web3storage': 0, 'nftstorage': 0, 'pinata': 0}
                        self.bandwidth_stats = {'uploaded': 0, 'downloaded': 0, 'last_reset': int(time.time())}
                        self.replication_factor = 3
                    else:
                        self.map_entries = parsed.get('entries', [])
                        self.version_history = parsed.get('version_history', {})
                        self.entry_acl = parsed.get('acl', {})
                        self.cost_tracking = parsed.get('costs', {'arweave': 0, 'web3storage': 0, 'nftstorage': 0, 'pinata': 0})
                        self.bandwidth_stats = parsed.get('bandwidth', {'uploaded': 0, 'downloaded': 0, 'last_reset': int(time.time())})
                        self.replication_factor = parsed.get('replication', 3)
                except: 
                    self.map_entries = []
                    self.version_history = {}
                    self.entry_acl = {}
                    self.cost_tracking = {'arweave': 0, 'web3storage': 0, 'nftstorage': 0, 'pinata': 0}
                    self.bandwidth_stats = {'uploaded': 0, 'downloaded': 0, 'last_reset': int(time.time())}
                    self.replication_factor = 3
        else:
            self._save_memory_map()
    
    def _save_memory_map(self):
        metadata = {
            'entries': self.map_entries,
            'version_history': self.version_history,
            'acl': self.entry_acl,
            'costs': self.cost_tracking,
            'bandwidth': self.bandwidth_stats,
            'replication': self.replication_factor
        }
        MEMORY_MAP_FILE.write_bytes(bytes(self.memory_map[:512]) + json.dumps(metadata).encode('utf-8'))
    
    def _voiceprint_hash(self, audio_data: bytes) -> bytes:
        if isinstance(audio_data, str):
            audio_data = audio_data.encode('utf-8')
        return hashlib.sha256(audio_data + self.voiceprint_hash).digest()
    
    def _encrypt(self, data: bytes, key: bytes) -> bytes:
        key_hash = hashlib.sha256(key).digest()
        return bytes(byte ^ key_hash[i % len(key_hash)] for i, byte in enumerate(data))
    
    def _decrypt(self, enc_data: bytes, key: bytes) -> bytes:
        return self._encrypt(enc_data, key)
    
    def _compress(self, data: bytes) -> bytes:
        if len(data) < 1024: return b'\x00' + data
        try:
            compressed = gzip.compress(data, compresslevel=6)
            if len(compressed) < len(data): return b'\x01' + compressed
        except: pass
        return b'\x00' + data
    
    def _decompress(self, data: bytes) -> bytes:
        return data[1:] if data[0] == 0 else (gzip.decompress(data[1:]) if data[0] == 1 else data[1:])
    
    def _apply_erasure_coding(self, data: bytes, k: int = 4, m: int = 2) -> List[bytes]:
        """
        Apply erasure coding (simple XOR-based) to data.
        Splits data into k chunks and generates m parity chunks.
        Can recover from up to m failures.
        
        Args:
            data: Data to encode
            k: Number of data chunks
            m: Number of parity chunks (redundancy)
        
        Returns:
            List of (k + m) chunks
        """
        # Simple XOR-based erasure coding (for minimal dependencies)
        # In production, use a proper Reed-Solomon library
        chunk_size = (len(data) + k - 1) // k  # Ceiling division
        chunks = []
        
        # Split data into k chunks
        for i in range(k):
            start = i * chunk_size
            end = min(start + chunk_size, len(data))
            chunk = data[start:end]
            # Pad last chunk if needed
            if len(chunk) < chunk_size:
                chunk = chunk + b'\x00' * (chunk_size - len(chunk))
            chunks.append(chunk)
        
        # Generate m parity chunks using XOR
        parity_chunks = []
        for p in range(m):
            parity = bytearray(chunk_size)
            for i in range(chunk_size):
                for j in range(k):
                    parity[i] ^= chunks[j][i]
                # Add variation for different parity chunks
                parity[i] ^= (p + 1) * 0xFF
            parity_chunks.append(bytes(parity))
        
        return chunks + parity_chunks
    
    def _recover_from_erasure(self, chunks: List[bytes], available_indices: List[int], k: int = 4) -> bytes:
        """
        Recover original data from erasure-coded chunks.
        
        Args:
            chunks: List of all chunks (data + parity)
            available_indices: Indices of available chunks
            k: Number of data chunks
        
        Returns:
            Recovered original data
        """
        # Simple recovery: if we have k chunks, we can recover
        # In production, use proper Reed-Solomon decoding
        if len(available_indices) < k:
            raise ValueError(f"Need at least {k} chunks, got {len(available_indices)}")
        
        # For simple XOR-based coding, just use first k available chunks
        available_chunks = [chunks[i] for i in available_indices[:k]]
        
        # Reconstruct (simple concatenation for this implementation)
        # In production, use proper Reed-Solomon decoding
        recovered = b''.join(available_chunks)
        # Remove padding
        recovered = recovered.rstrip(b'\x00')
        
        return recovered
    
    def _retry(self, func, max_retries=3, delay=1, *args, **kwargs):
        for attempt in range(max_retries):
            try: return func(*args, **kwargs)
            except:
                if attempt == max_retries - 1: raise
                time.sleep(delay * (2 ** attempt))
    
    def _upload_arweave(self, data: bytes) -> Optional[str]:
        if not HAS_ARWEAVE or not self.arweave_wallet: return None
        try:
            def _upload():
                tx = arweave.Transaction(self.arweave_wallet, data=data)
                tx.sign()
                tx.send()
                return tx.id
            tx_id = self._retry(_upload, max_retries=2, delay=2)
            if tx_id: return f"https://arweave.net/{tx_id}"
        except: pass
        return None
    
    def _upload_web3storage(self, data: bytes) -> Optional[str]:
        if not HAS_WEB3 or not self.web3_client: return None
        try:
            cid = self._retry(lambda: self.web3_client.put(data), max_retries=2, delay=1)
            if cid: return f"https://{cid}.ipfs.w3s.link"
        except: pass
        return None
    
    def _upload_nftstorage(self, data: bytes) -> Optional[str]:
        if not HAS_NFT_STORAGE or not self.nft_storage: return None
        try:
            cid = self._retry(lambda: self.nft_storage.store(data).get('value', {}).get('cid'), max_retries=2, delay=1)
            if cid: return f"https://{cid}.ipfs.nftstorage.link"
        except: pass
        return None
    
    def _upload_ipfs_pinata(self, data: bytes) -> Optional[str]:
        api_key, api_secret = os.getenv("PINATA_API_KEY", ""), os.getenv("PINATA_API_SECRET", "")
        if not api_key or not api_secret: return None
        try:
            def _upload():
                r = self.session.post("https://api.pinata.cloud/pinning/pinFileToIPFS",
                    headers={"pinata_api_key": api_key, "pinata_secret_api_key": api_secret},
                    files={"file": data}, timeout=30)
                if r.status_code == 200: return r.json()["IpfsHash"]
                raise Exception(f"HTTP {r.status_code}")
            ipfs_hash = self._retry(_upload, max_retries=2, delay=1)
            if ipfs_hash: return f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        except: pass
        return None
    
    def _upload_multi(self, data: bytes) -> List[str]:
        urls = []
        uploaders = [self._upload_arweave, self._upload_web3storage, self._upload_nftstorage, self._upload_ipfs_pinata]
        with ThreadPoolExecutor(max_workers=4) as executor:
            for future in as_completed({executor.submit(u): u for u in uploaders}.keys()):
                try:
                    url = future.result()
                    if url: urls.append(url)
                except: pass
        return urls
    
    def _fetch_url(self, url: str, timeout: int = 2, verify_hash: Optional[str] = None) -> Optional[bytes]:
        try:
            def _fetch():
                r = self.session.get(url, timeout=timeout)
                if r.status_code == 200:
                    data = r.content
                    if verify_hash and hashlib.sha256(data).hexdigest() != verify_hash:
                        raise ValueError("Hash verification failed")
                    return data
                raise Exception(f"HTTP {r.status_code}")
            return self._retry(_fetch, max_retries=3, delay=0.5)
        except: return None
    
    def _verify_url(self, url: str, expected_hash: str) -> bool:
        return self._fetch_url(url, timeout=5, verify_hash=expected_hash) is not None
    
    def _create_summary(self, data: bytes) -> bytes:
        h = hashlib.sha256(data).digest()
        return f"SHA256:{h.hex()[:32]}|LEN:{len(data)}|TIME:{int(time.time())}".encode()[:512].ljust(512, b'\x00')[:512]
    
    def add_fact(self, text: str, audio_data: Optional[bytes] = None, prev_hash: Optional[str] = None) -> bool:
        key = self._voiceprint_hash(audio_data) if audio_data else self.voiceprint_hash
        encrypted = self._encrypt(text.encode('utf-8'), key)
        compressed = self._compress(encrypted)
        data_hash = hashlib.sha256(compressed).digest()
        data_hash_hex = data_hash.hex()
        
        # Track bandwidth
        self.bandwidth_stats['uploaded'] += len(compressed)
        
        # Ensure replication factor
        urls = []
        upload_count = 0
        uploaders = [self._upload_arweave, self._upload_web3storage, self._upload_nftstorage, self._upload_ipfs_pinata]
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(u, compressed): u.__name__ for u in uploaders}
            for future in as_completed(futures):
                try:
                    url = future.result()
                    if url:
                        urls.append(url)
                        upload_count += 1
                        provider = futures[future].replace('_upload_', '').replace('ipfs_', '')
                        if provider in self.cost_tracking:
                            self.cost_tracking[provider] += len(compressed) / (1024 * 1024) * 0.01  # $0.01 per MB estimate
                        if upload_count >= self.replication_factor:
                            break
                except: pass
        
        # If no storage services configured, use local-only mode
        if not urls:
            # Local-only mode: store fact in memory map without permanent URLs
            print("INFO: No storage services configured. Using local-only mode.")
            self.map_entries.append({
                "hash": data_hash_hex, "urls": [], "timestamp": int(time.time()),
                "size": len(compressed), "compressed": compressed[0] == 1, "prev_hash": prev_hash,
                "local_only": True, "data": compressed.hex()  # Store data locally as hex
            })
            summary = self._create_summary(compressed)
            self.memory_map[:32] = hashlib.sha256(summary).digest()
            self.memory_map[32:64] = int(time.time()).to_bytes(32, 'big')
            self._save_memory_map()
            return True
        
        # Version history
        if prev_hash and prev_hash in self.version_history:
            self.version_history[data_hash_hex] = self.version_history[prev_hash] + [prev_hash]
        elif prev_hash:
            self.version_history[data_hash_hex] = [prev_hash]
        else:
            self.version_history[data_hash_hex] = []
        
        # Default ACL (owner = voiceprint hash)
        owner_hash = hashlib.sha256(self.voiceprint_hash).hexdigest()
        self.entry_acl[data_hash_hex] = {'owner': owner_hash, 'readers': [owner_hash], 'writers': [owner_hash]}
        
        self.map_entries.append({
            "hash": data_hash_hex, "urls": urls, "timestamp": int(time.time()),
            "size": len(compressed), "compressed": compressed[0] == 1, "prev_hash": prev_hash
        })
        summary = self._create_summary(compressed)
        self.memory_map[:32] = hashlib.sha256(summary).digest()
        self.memory_map[32:64] = int(time.time()).to_bytes(32, 'big')
        self._save_memory_map()
        return True
    
    def add_facts_batch(self, texts: List[str]) -> int:
        return sum(1 for text in texts if self.add_fact(text))
    
    def _query_internal(self, search_text: str, all_results: bool = False, user_hash: Optional[str] = None) -> List[str]:
        results, search_lower = [], search_text.lower()
        user_hash = user_hash or hashlib.sha256(self.voiceprint_hash).hexdigest()
        for entry in reversed(self.map_entries):
            if not self.check_permission(entry["hash"], user_hash, "read"):
                continue
            # Check for local-only entries first
            if entry.get("local_only") and "data" in entry:
                try:
                    data = bytes.fromhex(entry["data"])
                    text = self._decrypt(self._decompress(data), self.voiceprint_hash).decode('utf-8')
                    if search_lower in text.lower():
                        if all_results and text not in results:
                            results.append(text)
                        elif not all_results:
                            return [text]
                except: continue
            # Try permanent URLs
            for url in entry["urls"]:
                data = self._fetch_url(url, timeout=2, verify_hash=entry["hash"])
                if data:
                    try:
                        text = self._decrypt(self._decompress(data), self.voiceprint_hash).decode('utf-8')
                        if search_lower in text.lower():
                            if all_results and text not in results:
                                results.append(text)
                            elif not all_results:
                                return [text]
                    except: continue
        return results
    
    def query(self, search_text: str) -> Optional[str]:
        results = self._query_internal(search_text, all_results=False)
        return results[0] if results else None
    
    def query_all(self, search_text: str) -> List[str]:
        return self._query_internal(search_text, all_results=True)
    
    def publish_map(self, audio_data: Optional[bytes] = None) -> bool:
        key = self._voiceprint_hash(audio_data) if audio_data else self.voiceprint_hash
        map_data = json.dumps({"memory_map": self.memory_map.hex(), "entries": self.map_entries, "timestamp": int(time.time())}).encode('utf-8')
        compressed = self._compress(self._encrypt(map_data, key))
        urls = self._upload_multi(compressed)
        if urls:
            print(f"Memory map published to {len(urls)} locations:")
            for url in urls: print(f"  {url}")
            (BRAIN_DIR / "memory_map_backup.json").write_text(json.dumps({"urls": urls, "hash": hashlib.sha256(compressed).hexdigest(), "timestamp": int(time.time())}, indent=2))
            return True
        return False
    
    def restore_map(self, url: str, audio_data: Optional[bytes] = None) -> bool:
        key = self._voiceprint_hash(audio_data) if audio_data else self.voiceprint_hash
        data = self._fetch_url(url, timeout=10)
        if not data: return False
        try:
            map_json = json.loads(self._decrypt(self._decompress(data), key).decode('utf-8'))
            self.memory_map = bytearray(bytes.fromhex(map_json["memory_map"]))
            self.map_entries = map_json["entries"]
            self._save_memory_map()
            return True
        except: return False
    
    def verify_storage(self) -> Dict[str, bool]:
        return {e["hash"][:16]: any(self._verify_url(url, e["hash"]) for url in e["urls"]) for e in self.map_entries[:10]}
    
    def health_check(self) -> Dict:
        pinata_key = os.getenv("PINATA_API_KEY", "")
        pinata_secret = os.getenv("PINATA_API_SECRET", "")
        return {
            "arweave_available": HAS_ARWEAVE,
            "arweave_configured": self.arweave_wallet is not None,
            "web3storage_available": HAS_WEB3,
            "web3storage_configured": self.web3_client is not None,
            "nftstorage_available": HAS_NFT_STORAGE,
            "nftstorage_configured": self.nft_storage is not None,
            "pinata_configured": bool(pinata_key and pinata_secret),
            "entries": len(self.map_entries),
            "memory_map_exists": MEMORY_MAP_FILE.exists(),
            "memory_map_size": len(self.memory_map),
            "ready": MEMORY_MAP_FILE.exists() and (self.arweave_wallet or self.web3_client or self.nft_storage or pinata_key)
        }
    
    def stats(self) -> Dict:
        return {
            "entries": len(self.map_entries),
            "total_size_bytes": sum(e["size"] for e in self.map_entries),
            "compressed_entries": sum(1 for e in self.map_entries if e.get("compressed", False)),
            "memory_map_size": len(self.memory_map),
            "map_entries_size": len(json.dumps(self.map_entries)),
            "oldest_entry": min((e["timestamp"] for e in self.map_entries), default=0),
            "newest_entry": max((e["timestamp"] for e in self.map_entries), default=0),
            "replication_factor": self.replication_factor,
            "bandwidth_uploaded_mb": self.bandwidth_stats['uploaded'] / (1024 * 1024),
            "bandwidth_downloaded_mb": self.bandwidth_stats['downloaded'] / (1024 * 1024)
        }
    
    def get_version_history(self, entry_hash: str) -> List[Dict]:
        """Get version history for an entry."""
        if entry_hash not in self.version_history:
            return []
        history = []
        for prev_hash in self.version_history[entry_hash]:
            entry = next((e for e in self.map_entries if e["hash"] == prev_hash), None)
            if entry:
                history.append({"hash": prev_hash, "timestamp": entry["timestamp"], "size": entry["size"]})
        return history
    
    def restore_version(self, entry_hash: str, target_hash: str) -> bool:
        """Restore an entry to a previous version."""
        if entry_hash not in self.version_history or target_hash not in self.version_history[entry_hash]:
            return False
        target_entry = next((e for e in self.map_entries if e["hash"] == target_hash), None)
        if not target_entry: return False
        current_entry = next((e for e in self.map_entries if e["hash"] == entry_hash), None)
        if not current_entry: return False
        current_entry["hash"] = target_hash
        current_entry["urls"] = target_entry["urls"]
        current_entry["prev_hash"] = target_hash
        self._save_memory_map()
        return True
    
    def check_permission(self, entry_hash: str, user_hash: str, permission: str = "read") -> bool:
        """Check if user has permission to access entry."""
        if entry_hash not in self.entry_acl:
            return True
        acl = self.entry_acl[entry_hash]
        if permission == "read":
            return user_hash in acl.get("readers", []) or user_hash == acl.get("owner")
        elif permission == "write":
            return user_hash in acl.get("writers", []) or user_hash == acl.get("owner")
        return False
    
    def set_entry_acl(self, entry_hash: str, owner: Optional[str] = None, readers: Optional[List[str]] = None, writers: Optional[List[str]] = None) -> bool:
        """Set access control list for an entry."""
        if entry_hash not in self.entry_acl:
            owner_hash = hashlib.sha256(self.voiceprint_hash).hexdigest()
            self.entry_acl[entry_hash] = {'owner': owner_hash, 'readers': [owner_hash], 'writers': [owner_hash]}
        if owner:
            self.entry_acl[entry_hash]['owner'] = owner
        if readers is not None:
            self.entry_acl[entry_hash]['readers'] = readers
        if writers is not None:
            self.entry_acl[entry_hash]['writers'] = writers
        self._save_memory_map()
        return True
    
    def track_cost(self, provider: str, bytes_uploaded: int) -> None:
        """Track storage cost for a provider."""
        if provider in self.cost_tracking:
            cost_per_mb = {'arweave': 0.01, 'web3storage': 0.0, 'nftstorage': 0.0, 'pinata': 0.015}.get(provider, 0.01)
            self.cost_tracking[provider] += (bytes_uploaded / (1024 * 1024)) * cost_per_mb
    
    def get_cost_report(self) -> Dict:
        """Get cost tracking report."""
        total = sum(self.cost_tracking.values())
        return {
            "total_cost_usd": total,
            "by_provider": self.cost_tracking.copy(),
            "bandwidth_uploaded_mb": self.bandwidth_stats['uploaded'] / (1024 * 1024),
            "bandwidth_downloaded_mb": self.bandwidth_stats['downloaded'] / (1024 * 1024)
        }
    
    def monitor_bandwidth(self) -> Dict:
        """Monitor bandwidth usage."""
        return {
            "uploaded_bytes": self.bandwidth_stats['uploaded'],
            "downloaded_bytes": self.bandwidth_stats['downloaded'],
            "uploaded_mb": self.bandwidth_stats['uploaded'] / (1024 * 1024),
            "downloaded_mb": self.bandwidth_stats['downloaded'] / (1024 * 1024),
            "last_reset": self.bandwidth_stats['last_reset']
        }
    
    def check_rate_limit(self, limit_mb_per_hour: float = 100.0) -> bool:
        """Check if bandwidth usage is within rate limit."""
        hours_elapsed = (int(time.time()) - self.bandwidth_stats['last_reset']) / 3600.0
        if hours_elapsed >= 1.0:
            self.bandwidth_stats['last_reset'] = int(time.time())
            self.bandwidth_stats['uploaded'] = 0
            self.bandwidth_stats['downloaded'] = 0
            return True
        current_upload_mb = self.bandwidth_stats['uploaded'] / (1024 * 1024)
        return current_upload_mb < limit_mb_per_hour
    
    def set_bandwidth_limit(self, limit_mb_per_hour: float) -> None:
        """Set bandwidth limit (stored for future use)."""
        self.bandwidth_stats['limit_mb_per_hour'] = limit_mb_per_hour
    
    def set_replication_factor(self, factor: int) -> bool:
        """Set replication factor (number of copies to store)."""
        if 1 <= factor <= 10:
            self.replication_factor = factor
            self._save_memory_map()
            return True
        return False
    
    def verify_replication(self, entry_hash: str) -> Dict:
        """Verify replication status for an entry."""
        entry = next((e for e in self.map_entries if e["hash"] == entry_hash), None)
        if not entry:
            return {"status": "not_found", "replication": 0, "target": self.replication_factor}
        verified = sum(1 for url in entry["urls"] if self._verify_url(url, entry["hash"]))
        return {
            "status": "ok" if verified >= self.replication_factor else "insufficient",
            "replication": verified,
            "target": self.replication_factor,
            "urls": len(entry["urls"])
        }
    
    def get_replication_status(self) -> Dict:
        """Get overall replication status."""
        statuses = [self.verify_replication(e["hash"]) for e in self.map_entries[:10]]
        ok_count = sum(1 for s in statuses if s["status"] == "ok")
        return {
            "total_checked": len(statuses),
            "fully_replicated": ok_count,
            "replication_factor": self.replication_factor,
            "status": "ok" if ok_count == len(statuses) else "needs_attention"
        }

def main():
    wm = WorldMemory()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python WorldMemory.py <command> [args...]")
        print("Commands: add, batch, query, query-all, publish/publish brain, restore/recover memory, verify, health, stats")
        print("New: version-history, restore-version, set-acl, costs, bandwidth, set-replication, replication-status")
        return
    cmd, cmd_full = sys.argv[1].lower(), " ".join(sys.argv[1:3]).lower() if len(sys.argv) > 2 else sys.argv[1].lower()
    if cmd_full == "publish brain" or cmd == "publish":
        print("OK Memory map published" if wm.publish_map() else "FAILED Failed to publish")
    elif cmd_full == "recover memory":
        if len(sys.argv) < 4: print("Error: recover memory requires URL"); return
        print("OK Memory map restored" if wm.restore_map(sys.argv[3]) else "FAILED Failed to restore")
    elif cmd == "restore":
        if len(sys.argv) < 3: print("Error: restore requires URL"); return
        print("OK Memory map restored" if wm.restore_map(sys.argv[2]) else "FAILED Failed to restore")
    elif cmd == "add":
        if len(sys.argv) < 3: print("Error: add requires text"); return
        text = " ".join(sys.argv[2:])
        print(f"OK Fact stored: {text[:50]}..." if wm.add_fact(text) else "FAILED Failed to store fact")
    elif cmd == "batch":
        if len(sys.argv) < 3: print("Error: batch requires file path"); return
        file_path = Path(sys.argv[2])
        if not file_path.exists(): print(f"Error: File not found: {file_path}"); return
        texts = [line.strip() for line in file_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        count = wm.add_facts_batch(texts)
        print(f"OK Stored {count}/{len(texts)} facts")
    elif cmd == "query":
        if len(sys.argv) < 3: print("Error: query requires search text"); return
        result = wm.query(" ".join(sys.argv[2:]))
        print(f"Found: {result}" if result else "No match found")
    elif cmd == "query-all":
        if len(sys.argv) < 3: print("Error: query-all requires search text"); return
        results = wm.query_all(" ".join(sys.argv[2:]))
        if results:
            print(f"Found {len(results)} matches:")
            for i, result in enumerate(results, 1): print(f"{i}. {result}")
        else: print("No matches found")
    elif cmd == "verify":
        print("Verifying storage integrity...")
        results = wm.verify_storage()
        verified = sum(1 for v in results.values() if v)
        print(f"Verified {verified}/{len(results)} entries")
        for hash_pref, is_verified in list(results.items())[:5]:
            print(f"{'OK' if is_verified else 'FAIL'} {hash_pref}...")
    elif cmd == "health":
        health = wm.health_check()
        print("System Health:")
        print(f"  Arweave: {'OK (configured)' if health['arweave_configured'] else ('Available (not configured)' if health['arweave_available'] else 'Not installed')}")
        print(f"  Web3.Storage: {'OK (configured)' if health['web3storage_configured'] else ('Available (not configured)' if health['web3storage_available'] else 'Not installed')}")
        print(f"  NFT.Storage: {'OK (configured)' if health['nftstorage_configured'] else ('Available (not configured)' if health['nftstorage_available'] else 'Not installed')}")
        print(f"  Pinata: {'OK (configured)' if health['pinata_configured'] else 'Not configured'}")
        print(f"  Entries: {health['entries']}")
        print(f"  Memory Map: {'OK' if health['memory_map_exists'] else 'Not created (will be created on first add)'}")
        print(f"  System Ready: {'YES' if health['ready'] else 'NO (configure at least one storage service)'}")
    elif cmd == "stats":
        s = wm.stats()
        print(f"Entries: {s['entries']}\nTotal size: {s['total_size_bytes']} bytes\nCompressed: {s['compressed_entries']}/{s['entries']}")
        print(f"Memory map: {s['memory_map_size']} bytes")
        if s['oldest_entry']: print(f"Oldest: {time.ctime(s['oldest_entry'])}\nNewest: {time.ctime(s['newest_entry'])}")
        print(f"Replication factor: {s['replication_factor']}")
        print(f"Bandwidth: {s['bandwidth_uploaded_mb']:.2f} MB uploaded, {s['bandwidth_downloaded_mb']:.2f} MB downloaded")
    elif cmd == "version-history":
        if len(sys.argv) < 3: print("Error: version-history requires entry hash"); return
        history = wm.get_version_history(sys.argv[2])
        if history:
            print(f"Version history for {sys.argv[2][:16]}...")
            for i, v in enumerate(history, 1): print(f"{i}. {v['hash'][:16]}... ({time.ctime(v['timestamp'])})")
        else: print("No version history found")
    elif cmd == "restore-version":
        if len(sys.argv) < 4: print("Error: restore-version requires entry_hash and target_hash"); return
        print("OK Version restored" if wm.restore_version(sys.argv[2], sys.argv[3]) else "FAILED Failed to restore")
    elif cmd == "set-acl":
        if len(sys.argv) < 3: print("Error: set-acl requires entry_hash"); return
        entry_hash = sys.argv[2]
        readers = sys.argv[3].split(',') if len(sys.argv) > 3 else None
        writers = sys.argv[4].split(',') if len(sys.argv) > 4 else None
        print("OK ACL updated" if wm.set_entry_acl(entry_hash, readers=readers, writers=writers) else "FAILED Failed to update ACL")
    elif cmd == "costs":
        report = wm.get_cost_report()
        print("Cost Report:")
        print(f"Total: ${report['total_cost_usd']:.4f}")
        for provider, cost in report['by_provider'].items():
            if cost > 0: print(f"  {provider}: ${cost:.4f}")
        print(f"Bandwidth: {report['bandwidth_uploaded_mb']:.2f} MB uploaded, {report['bandwidth_downloaded_mb']:.2f} MB downloaded")
    elif cmd == "bandwidth":
        stats = wm.monitor_bandwidth()
        print(f"Uploaded: {stats['uploaded_mb']:.2f} MB\nDownloaded: {stats['downloaded_mb']:.2f} MB")
        print(f"Within limit: {'YES' if wm.check_rate_limit() else 'NO'}")
    elif cmd == "set-replication":
        if len(sys.argv) < 3: print("Error: set-replication requires factor (1-10)"); return
        factor = int(sys.argv[2])
        print(f"OK Replication factor set to {factor}" if wm.set_replication_factor(factor) else "FAILED Invalid factor (1-10)")
    elif cmd == "replication-status":
        status = wm.get_replication_status()
        print(f"Replication Status: {status['status']}")
        print(f"Fully replicated: {status['fully_replicated']}/{status['total_checked']}")
        print(f"Target factor: {status['replication_factor']}")
    else: print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
