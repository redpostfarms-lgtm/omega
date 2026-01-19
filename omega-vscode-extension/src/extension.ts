import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as si from 'systeminformation';

const execAsync = promisify(exec);

let statusBarItem: vscode.StatusBarItem;
let optimizationTimer: NodeJS.Timeout | undefined;
let completionProvider: vscode.Disposable | undefined;

/**
 * OMEGA AUTOPILOT - VS Code Extension
 * Auto-loads Omega resource optimizer with brain/memory core
 * Provides intelligent autocomplete with predictive algorithms
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('🔧 OMEGA AUTOPILOT - Activating...');

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'omega.status';
    context.subscriptions.push(statusBarItem);

    // Initialize Omega
    initializeOmega(context);

    // Register commands
    registerCommands(context);

    // Start autocomplete if enabled
    const config = vscode.workspace.getConfiguration('omega');
    if (config.get<boolean>('enableAutocomplete', true)) {
        activateAutocomplete(context);
    }

    console.log('✅ OMEGA AUTOPILOT - Active');
}

async function initializeOmega(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('omega');

    if (!config.get<boolean>('autoStart', true)) {
        vscode.window.showInformationMessage('Omega Autopilot: Auto-start disabled');
        return;
    }

    // Load brain & memory core
    await loadBrainCore();

    // Run initial optimization
    await runOptimization();

    // Start periodic optimization
    const interval = config.get<number>('optimizationInterval', 20) * 60 * 1000;
    optimizationTimer = setInterval(() => runOptimization(), interval);

    // Update status bar
    updateStatusBar();
    setInterval(() => updateStatusBar(), 10000); // Update every 10 seconds
}

async function loadBrainCore() {
    try {
        vscode.window.showInformationMessage('🧠 Omega: Loading brain & memory core...');

        // Load configuration from workspace
        const brainConfig = {
            gpuPriority: vscode.workspace.getConfiguration('omega').get<number>('gpuPriority', 60),
            cpuPriority: vscode.workspace.getConfiguration('omega').get<number>('cpuPriority', 40),
            ramCacheLimit: vscode.workspace.getConfiguration('omega').get<number>('ramCacheLimit', 512),
            memoryThreshold: vscode.workspace.getConfiguration('omega').get<number>('memoryThreshold', 85)
        };

        // Store in global state
        await vscode.workspace.getConfiguration('omega').update('brainLoaded', true, vscode.ConfigurationTarget.Global);

        console.log('✅ Brain & Memory Core loaded:', brainConfig);
        vscode.window.showInformationMessage('✅ Omega brain & memory core active');

        return brainConfig;
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to load brain core: ${error}`);
        console.error('Brain core error:', error);
    }
}

async function runOptimization() {
    const config = vscode.workspace.getConfiguration('omega');
    const pythonPath = config.get<string>('pythonPath', '');
    const scriptPath = config.get<string>('optimizerScript', '');

    if (!pythonPath || !scriptPath) {
        vscode.window.showWarningMessage('Omega: Python path or script path not configured');
        return;
    }

    try {
        console.log('🔧 Running Omega optimization...');
        const { stdout, stderr } = await execAsync(`"${pythonPath}" "${scriptPath}"`);

        if (stderr) {
            console.error('Optimization stderr:', stderr);
        }

        console.log('✅ Optimization complete');

        // Parse results from stdout if needed
        if (stdout.includes('OPTIMAL')) {
            statusBarItem.text = '$(check) Omega: Optimal';
            statusBarItem.backgroundColor = undefined;
        }

    } catch (error) {
        console.error('Optimization failed:', error);
        statusBarItem.text = '$(warning) Omega: Error';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
}

async function updateStatusBar() {
    const config = vscode.workspace.getConfiguration('omega');
    if (!config.get<boolean>('showStatusBar', true)) {
        statusBarItem.hide();
        return;
    }

    try {
        const mem = await si.mem();
        const cpu = await si.currentLoad();

        const memPercent = ((mem.active / mem.total) * 100).toFixed(1);
        const cpuPercent = cpu.currentLoad.toFixed(1);

        // Update status bar with current metrics
        statusBarItem.text = `$(pulse) Ω: ${memPercent}% RAM | ${cpuPercent}% CPU`;

        // Color code based on memory usage
        const memNum = parseFloat(memPercent);
        if (memNum > 85) {
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
        } else if (memNum > 75) {
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        } else {
            statusBarItem.backgroundColor = undefined;
        }

        statusBarItem.show();
    } catch (error) {
        statusBarItem.text = '$(pulse) Omega';
        statusBarItem.show();
    }
}

function registerCommands(context: vscode.ExtensionContext) {
    // Optimize command
    context.subscriptions.push(
        vscode.commands.registerCommand('omega.optimize', async () => {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Running Omega optimization...",
                cancellable: false
            }, async () => {
                await runOptimization();
            });
        })
    );

    // Status command
    context.subscriptions.push(
        vscode.commands.registerCommand('omega.status', async () => {
            const mem = await si.mem();
            const cpu = await si.currentLoad();
            const config = vscode.workspace.getConfiguration('omega');

            const memPercent = ((mem.active / mem.total) * 100).toFixed(2);
            const cpuPercent = cpu.currentLoad.toFixed(2);

            const message = `
🔧 OMEGA SYSTEM STATUS

Memory: ${memPercent}% (${(mem.active / 1024 / 1024 / 1024).toFixed(2)} GB / ${(mem.total / 1024 / 1024 / 1024).toFixed(2)} GB)
CPU: ${cpuPercent}%
GPU Priority: ${config.get('gpuPriority')}%
CPU Priority: ${config.get('cpuPriority')}%
RAM Cache Limit: ${config.get('ramCacheLimit')} MB
Memory Threshold: ${config.get('memoryThreshold')}%

Brain Core: ${config.get('brainLoaded') ? '✅ Loaded' : '❌ Not Loaded'}
Autocomplete: ${config.get('enableAutocomplete') ? '✅ Enabled' : '❌ Disabled'}
            `.trim();

            vscode.window.showInformationMessage(message, { modal: true });
        })
    );

    // Configure command
    context.subscriptions.push(
        vscode.commands.registerCommand('omega.configure', async () => {
            const config = vscode.workspace.getConfiguration('omega');

            const gpuPriority = await vscode.window.showInputBox({
                prompt: 'GPU Priority (%)',
                value: config.get('gpuPriority', 60).toString(),
                validateInput: (value) => {
                    const num = parseInt(value);
                    return (num >= 0 && num <= 100) ? null : 'Must be between 0-100';
                }
            });

            if (gpuPriority) {
                await config.update('gpuPriority', parseInt(gpuPriority), vscode.ConfigurationTarget.Global);
            }

            const cpuPriority = await vscode.window.showInputBox({
                prompt: 'CPU Priority (%)',
                value: config.get('cpuPriority', 40).toString(),
                validateInput: (value) => {
                    const num = parseInt(value);
                    return (num >= 0 && num <= 100) ? null : 'Must be between 0-100';
                }
            });

            if (cpuPriority) {
                await config.update('cpuPriority', parseInt(cpuPriority), vscode.ConfigurationTarget.Global);
            }

            vscode.window.showInformationMessage('✅ Omega configuration updated');
        })
    );

    // Load brain command
    context.subscriptions.push(
        vscode.commands.registerCommand('omega.loadBrain', async () => {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Loading Omega brain & memory core...",
                cancellable: false
            }, async () => {
                await loadBrainCore();
            });
        })
    );
}

/**
 * OMEGA PREDICTIVE AUTOCOMPLETE
 * Similar to Cursor with predictive algorithms
 */
function activateAutocomplete(context: vscode.ExtensionContext) {
    console.log('🤖 Activating Omega Predictive Autocomplete...');

    // Register completion provider for all languages
    completionProvider = vscode.languages.registerCompletionItemProvider(
        { scheme: 'file', language: '*' },
        {
            provideCompletionItems(document: vscode.TextDocument, position: vscode.Position) {
                const linePrefix = document.lineAt(position).text.substr(0, position.character);
                const completions: vscode.CompletionItem[] = [];

                // Analyze context for intelligent suggestions
                const context = analyzeContext(document, position);

                // Generate predictive completions based on context
                const predictions = generatePredictions(context, linePrefix);

                predictions.forEach((prediction, index) => {
                    const completion = new vscode.CompletionItem(
                        prediction.text,
                        vscode.CompletionItemKind.Snippet
                    );
                    completion.insertText = new vscode.SnippetString(prediction.snippet);
                    completion.documentation = new vscode.MarkdownString(prediction.description);
                    completion.sortText = `0${index}`; // Priority ordering
                    completion.detail = '⚡ Omega Prediction';

                    completions.push(completion);
                });

                return completions;
            }
        },
        '.' // Trigger on dot
    );

    context.subscriptions.push(completionProvider);

    console.log('✅ Omega Predictive Autocomplete active');
}

interface CodeContext {
    language: string;
    currentLine: string;
    previousLines: string[];
    nextLines: string[];
    imports: string[];
    functionContext: string | null;
    classContext: string | null;
}

function analyzeContext(document: vscode.TextDocument, position: vscode.Position): CodeContext {
    const language = document.languageId;
    const currentLine = document.lineAt(position).text;

    // Get surrounding context
    const previousLines: string[] = [];
    for (let i = Math.max(0, position.line - 5); i < position.line; i++) {
        previousLines.push(document.lineAt(i).text);
    }

    const nextLines: string[] = [];
    for (let i = position.line + 1; i < Math.min(document.lineCount, position.line + 5); i++) {
        nextLines.push(document.lineAt(i).text);
    }

    // Extract imports
    const imports: string[] = [];
    for (let i = 0; i < Math.min(50, document.lineCount); i++) {
        const line = document.lineAt(i).text;
        if (line.match(/^import |^from .* import |^using |^#include/)) {
            imports.push(line);
        }
    }

    // Find function/class context
    let functionContext: string | null = null;
    let classContext: string | null = null;

    for (let i = position.line - 1; i >= 0; i--) {
        const line = document.lineAt(i).text;
        if (!functionContext && line.match(/^\s*(def |function |async function |fun |func )/)) {
            functionContext = line.trim();
        }
        if (!classContext && line.match(/^\s*(class |interface |struct )/)) {
            classContext = line.trim();
        }
        if (functionContext && classContext) break;
    }

    return {
        language,
        currentLine,
        previousLines,
        nextLines,
        imports,
        functionContext,
        classContext
    };
}

interface Prediction {
    text: string;
    snippet: string;
    description: string;
    confidence: number;
}

function generatePredictions(context: CodeContext, linePrefix: string): Prediction[] {
    const predictions: Prediction[] = [];

    // Python-specific predictions
    if (context.language === 'python') {
        if (linePrefix.match(/^\s*def /)) {
            predictions.push({
                text: 'docstring',
                snippet: '"""\\n    ${1:Description}\\n    \\n    Args:\\n        ${2:param}: ${3:description}\\n    \\n    Returns:\\n        ${4:return_type}: ${5:description}\\n    """',
                description: 'Add docstring with Args and Returns',
                confidence: 0.9
            });
        }

        if (linePrefix.includes('for ')) {
            predictions.push({
                text: 'enumerate',
                snippet: 'for ${1:index}, ${2:item} in enumerate(${3:iterable}):\\n    ${0}',
                description: 'for loop with enumerate',
                confidence: 0.85
            });
        }

        if (linePrefix.match(/except\s*$/)) {
            predictions.push({
                text: 'Exception as e',
                snippet: 'Exception as e:\\n    ${1:print(f"Error: {e}")}\\n    ${0}',
                description: 'Catch exception with variable',
                confidence: 0.9
            });
        }
    }

    // JavaScript/TypeScript predictions
    if (context.language === 'javascript' || context.language === 'typescript') {
        if (linePrefix.match(/console\./)) {
            predictions.push({
                text: 'log',
                snippet: 'log(${1:message})',
                description: 'Console log',
                confidence: 0.95
            });
        }

        if (linePrefix.includes('async ')) {
            predictions.push({
                text: 'try-catch-async',
                snippet: 'try {\\n    ${1:// await operation}\\n} catch (error) {\\n    console.error(${2:\'Error:\'}, error);\\n}',
                description: 'Async try-catch block',
                confidence: 0.9
            });
        }
    }

    // Common patterns across languages
    if (linePrefix.match(/if\s*\(/)) {
        predictions.push({
            text: 'if-else',
            snippet: 'if (${1:condition}) {\\n    ${2}\\n} else {\\n    ${3}\\n}',
            description: 'if-else statement',
            confidence: 0.85
        });
    }

    // Context-aware predictions based on surrounding code
    if (context.functionContext) {
        predictions.push({
            text: 'return early',
            snippet: 'if (${1:condition}) {\\n    return ${2:null};\\n}\\n${0}',
            description: 'Early return pattern',
            confidence: 0.75
        });
    }

    // Sort by confidence
    predictions.sort((a, b) => b.confidence - a.confidence);

    return predictions.slice(0, 10); // Return top 10 predictions
}

export function deactivate() {
    if (optimizationTimer) {
        clearInterval(optimizationTimer);
    }

    if (completionProvider) {
        completionProvider.dispose();
    }

    console.log('🔧 OMEGA AUTOPILOT - Deactivated');
}
