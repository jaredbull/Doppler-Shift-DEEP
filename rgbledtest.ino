const int red = 12;
const int green = 11;
const int blue = 10;

int incomingByte;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  pinMode(blue, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte == 'W') {
      analogWrite(red, 0);
      analogWrite(green, 0);
      analogWrite(blue, 0);
    }
    if (incomingByte == 'R') {
      analogWrite(red, 0);
      analogWrite(green, 255);
      analogWrite(blue, 255);
    }
    if (incomingByte == 'B') {
      analogWrite(red, 255);
      analogWrite(green, 255);
      analogWrite(blue, 0);
    }
    if (incomingByte == 'O') {
      analogWrite(red, 255);
      analogWrite(green, 255);
      analogWrite(blue, 255);
    }
  }
}
