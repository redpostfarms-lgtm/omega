/**
 * QCAD ECMAScript Tool Template
 * Generated for: AutoCAD Designs Unified System
 * Location: 06_AutoCAD_Automation\qcad\scripts\
 *
 * This template provides:
 * - Menu/command registration placeholder
 * - Entity creation placeholder
 * - Layer enforcement placeholder
 *
 * Customize this template for your specific automation task.
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

var PROJECT_NAME = "ProjectName";
var UNITS = "mm";  // or "in" for inches
var SCALE = 1.0;

// Layer standards (reference LAYER_STANDARD.json)
var LAYERS = {
    "A-WALL": {color: 1, lineweight: 50},      // Red, 0.50mm
    "A-DOOR": {color: 3, lineweight: 25},      // Green, 0.25mm
    "A-WINDOW": {color: 5, lineweight: 25},     // Blue, 0.25mm
    "A-DIM": {color: 2, lineweight: 13},        // Yellow, 0.13mm
    "CONSTRUCTION": {color: 8, lineweight: 13}   // Gray, 0.13mm
};

// Export paths (relative to AutoCAD Designs root)
var EXPORT_BASE = "C:\\Users\\Drakalich\\Desktop\\AutoCAD Designs\\05_Exports\\";

// ============================================================================
// LAYER ENFORCEMENT
// ============================================================================

/**
 * Apply layer standards to an entity.
 * 
 * @param {REntity} entity - QCAD entity object
 * @param {String} layerName - Layer name from LAYERS dict
 */
function applyLayerStandards(entity, layerName) {
    if (LAYERS.hasOwnProperty(layerName)) {
        var layer = LAYERS[layerName];
        
        // Set layer
        var layerId = getOrCreateLayer(layerName);
        entity.setLayerId(layerId);
        
        // Set color (QCAD color index)
        entity.setColor(new RColor(layer.color));
        
        // Set lineweight (in 1/100 mm)
        entity.setLineweight(layer.lineweight);
        
        EAction.handleUserMessage("Applied layer: " + layerName);
    } else {
        EAction.handleUserWarning("Layer not found: " + layerName);
    }
}

/**
 * Get or create a layer by name.
 * 
 * @param {String} layerName - Layer name
 * @returns {Number} Layer ID
 */
function getOrCreateLayer(layerName) {
    var doc = EAction.getDocument();
    var di = EAction.getDocumentInterface();
    
    // Check if layer exists
    var layerId = di.getLayerId(layerName);
    if (layerId === RLayer.INVALID_ID) {
        // Create new layer
        var layer = new RLayer(doc, layerName);
        layerId = di.addLayer(layer);
        EAction.handleUserMessage("Created layer: " + layerName);
    }
    
    return layerId;
}

// ============================================================================
// ENTITY CREATION (CUSTOMIZE HERE)
// ============================================================================

/**
 * Create example geometry.
 * Customize this function for your specific task.
 */
function createGeometry() {
    var doc = EAction.getDocument();
    var di = EAction.getDocumentInterface();
    
    // Example: Create a line
    var startPoint = new RVector(0, 0);
    var endPoint = new RVector(100, 100);
    var line = new RLineEntity(doc, new RLineData(startPoint, endPoint));
    
    // Apply layer standards
    applyLayerStandards(line, "A-WALL");
    
    // Add to document
    var op = new RAddObjectOperation(line);
    di.applyOperation(op);
    
    EAction.handleUserMessage("Geometry created");
}

// ============================================================================
// EXPORT HELPERS (PLACEHOLDER)
// ============================================================================

/**
 * Export document to DXF format.
 * 
 * @param {String} filename - Output filename (without extension)
 */
function exportDXF(filename) {
    var exportPath = EXPORT_BASE + "DXF\\" + filename + ".dxf";
    // TODO: Implement DXF export
    // Use RFileExporterAdapter or similar
    EAction.handleUserMessage("Export DXF to: " + exportPath);
}

/**
 * Export document to PDF format.
 * 
 * @param {String} filename - Output filename (without extension)
 */
function exportPDF(filename) {
    var exportPath = EXPORT_BASE + "PDF\\" + filename + ".pdf";
    // TODO: Implement PDF export
    // Use RFileExporterAdapter or similar
    EAction.handleUserMessage("Export PDF to: " + exportPath);
}

// ============================================================================
// MENU/COMMAND REGISTRATION (PLACEHOLDER)
// ============================================================================

/**
 * Initialize the tool (called when script loads).
 */
function init() {
    // Register menu action
    var action = new RGuiAction("AutoCAD Designs Tool", this);
    action.setRequiresDocument(true);
    action.setScriptFile("_tool_template.js");
    action.setGroupSortOrder(90000);  // Sort order in menu
    action.setSortOrder(100);
    action.setWidgetNames(["MiscDrawMenu"]);
    
    // Connect to main function
    action.triggered.connect(main);
    
    // Add to menu
    EAction.addGuiAction(action);
    EAction.addToolToMenu(action);
}

/**
 * Main function (called when menu item is clicked).
 */
function main() {
    EAction.handleUserMessage("=".repeat(60));
    EAction.handleUserMessage("QCAD Tool Template");
    EAction.handleUserMessage("=".repeat(60));
    
    // Create geometry
    createGeometry();
    
    // Export (uncomment as needed)
    // exportDXF(PROJECT_NAME + "_export");
    // exportPDF(PROJECT_NAME + "_export");
    
    EAction.handleUserMessage("=".repeat(60));
    EAction.handleUserMessage("Tool execution complete");
    EAction.handleUserMessage("=".repeat(60));
}

// Auto-initialize when script loads
init();

