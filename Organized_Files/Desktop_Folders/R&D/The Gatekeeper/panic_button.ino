// Physical Panic Button
// Cheap $6 Arduino Leonardo on USB
// Press once → same scorched-earth sequence

// Pin configuration
const int BUTTON_PIN = 2;
const int LED_PIN = 13;

// State
bool buttonPressed = false;
unsigned long lastPress = 0;
const unsigned long DEBOUNCE_DELAY = 200;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  
  Serial.begin(9600);
  Serial.println("Gatekeeper Panic Button Ready");
  
  // Initialize as keyboard (Leonardo only)
  Keyboard.begin();
}

void loop() {
  // Read button state
  bool currentState = !digitalRead(BUTTON_PIN);  // Inverted due to pullup
  
  // Debounce
  if (currentState && !buttonPressed && (millis() - lastPress > DEBOUNCE_DELAY)) {
    buttonPressed = true;
    lastPress = millis();
    
    // Flash LED
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    
    // Send keyboard command to trigger scorched earth
    // This opens command prompt and runs the script
    Keyboard.press(KEY_LEFT_GUI);  // Windows key
    Keyboard.press('r');            // Run dialog
    Keyboard.releaseAll();
    delay(100);
    
    // Type command
    Keyboard.print("python \"D:\\RPF_BRAIN\\The Gatekeeper\\scorched_earth.py\"");
    Keyboard.press(KEY_RETURN);
    Keyboard.releaseAll();
    
    Serial.println("Panic button activated!");
    
    // Flash LED rapidly
    for (int i = 0; i < 10; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(50);
      digitalWrite(LED_PIN, LOW);
      delay(50);
    }
  }
  
  if (!currentState) {
    buttonPressed = false;
  }
  
  delay(10);
}

