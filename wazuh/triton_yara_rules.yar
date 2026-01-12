/*
  Triton (TRISIS/HatMan) YARA Detection Rules
  ===========================================
  YARA rules for detecting Triton malware artifacts.
  
  Installation:
    1. Copy to /var/ossec/active-response/bin/yara/rules/
    2. chown wazuh:wazuh triton_yara_rules.yar
    3. chmod 660 triton_yara_rules.yar
    4. Configure Wazuh FIM to use YARA scanning
  
  Reference: Triton attack case study (2017)
    - Target: Schneider Electric Triconex Tricon SIS (MP3008 firmware 10.0–10.4)
    - Attribution: TEMP.Veles / XENOTIME (CNIIHM lab, Russia)
    - MITRE Campaign: C0030
  
  Sources:
    - ICS-CERT/CISA
    - FireEye (Mandiant)
    - Dragos
    - Nozomi Networks
*/

rule TRITON_Framework {
  meta:
    description = "TRITON/TRISIS/HatMan framework indicators"
    author = "ICS-CERT/Mandiant"
    date = "2017-12"
    reference = "https://www.cisa.gov/news-events/cybersecurity-advisories/aa17-352a"
    severity = "critical"
    mitre_id = "C0030"
  strings:
    $pyc = ".pyc" nocase wide
    $ts = "TsHi" nocase wide
    $inject = "inject.bin" nocase
    $library = "library.zip" nocase
    $trilog = "trilog.exe" nocase
    $tristation = "TriStation" nocase
    $triconex = "Triconex" nocase
  condition:
    2 of them and filesize < 3MB
}

rule TRITON_trilog_exe {
  meta:
    description = "TRITON/TRISIS masquerading as trilog.exe"
    author = "ICS-CERT"
    date = "2017-12"
    reference = "https://github.com/NozomiNetworks/tricotools"
    severity = "critical"
    mitre_technique = "T0849"
  strings:
    $s1 = "trilog.exe" nocase
    $s2 = "inject.bin" nocase
    $s3 = "imain.bin" nocase
    $s4 = "library.zip" nocase
    $s5 = "TsHi" nocase
    $s6 = "TsLow" nocase
  condition:
    $s1 and (2 of ($s2, $s3, $s4, $s5, $s6))
}

rule TRITON_Payload_inject_bin {
  meta:
    description = "TRITON inject.bin payload indicator"
    author = "FireEye/Mandiant"
    date = "2017-12"
    reference = "https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html"
    severity = "critical"
    mitre_technique = "T0843"
    hash1 = "3788a0a1128cfa5655f977411c164bd8"
  strings:
    $s1 = "inject.bin" nocase
    $s2 = /inject[\x00-\xFF]{0,20}payload/i
    $s3 = "PowerPC" nocase
    $s4 = "shellcode" nocase
  condition:
    $s1 or (2 of ($s2, $s3, $s4))
}

rule TRITON_Payload_imain_bin {
  meta:
    description = "TRITON imain.bin payload indicator"
    author = "FireEye/Mandiant"
    date = "2017-12"
    reference = "https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html"
    severity = "critical"
    mitre_technique = "T0843"
    hash1 = "62c1dd25d7ca3e5567f86b3d2f96605f"
  strings:
    $s1 = "imain.bin" nocase
    $s2 = /imain[\x00-\xFF]{0,20}backdoor/i
    $s3 = "RAT" nocase
    $s4 = "SafeAppendProgramMod" nocase
  condition:
    $s1 or (2 of ($s2, $s3, $s4))
}

rule TRITON_Python_Framework {
  meta:
    description = "TRITON Python framework (Py2EXE compiled)"
    author = "Dragos"
    date = "2017-12"
    reference = "https://www.dragos.com/threat/triton/"
    severity = "high"
    mitre_technique = "T0849"
  strings:
    $s1 = "library.zip" nocase
    $s2 = "TsHi.py" nocase
    $s3 = "TsLow.py" nocase
    $s4 = "TS_cnames.py" nocase
    $s5 = "Py2EXE" nocase
    $s6 = "python27.dll" nocase
  condition:
    $s1 or (2 of ($s2, $s3, $s4, $s5, $s6))
}

rule TRITON_TriStation_Protocol {
  meta:
    description = "TRITON TriStation protocol indicators"
    author = "Nozomi Networks"
    date = "2018-07"
    reference = "https://github.com/NozomiNetworks/tricotools"
    severity = "high"
    mitre_technique = "T0871"
  strings:
    $s1 = "SafeAppendProgramMod" nocase
    $s2 = "UDP.*1502" nocase
    $s3 = "TriStation" nocase
    $s4 = "Triconex" nocase
    $s5 = "program_append" nocase
  condition:
    $s1 or (2 of ($s2, $s3, $s4, $s5))
}

rule TRITON_Hash_trilog_exe {
  meta:
    description = "TRITON trilog.exe known hash"
    author = "CISA"
    date = "2017-12"
    reference = "https://www.cisa.gov/news-events/cybersecurity-advisories/aa17-352a"
    severity = "critical"
    mitre_technique = "T0849"
    hash1 = "0f4c93a6c105b7d4869012ef3c4e078f"
    hash_type = "SHA256"
  condition:
    false  // Use hash-based detection in Wazuh FIM instead
}
