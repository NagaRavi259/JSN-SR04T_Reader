/* ****************************************************
* @brief Water-proof Ultrasonic Sensor (ULS)

 * @copyright   [DFRobot](http://www.dfrobot.com), 2016
 * @copyright   GNU Lesser General Public License

* @author [huyujie](yujie.hu@dfrobot.com)
* @version  V1.0
* @date  2020-12-7

* GNU Lesser General Public License.
* All above must be included in any redistribution
* ****************************************************/

#include <SoftwareSerial.h>
unsigned char buffer_RTT[4] = {0};// Used to store data read from the serial port
int Distance = 0;//Used to store the read distance value
unsigned char CS;//Save checksum
SoftwareSerial mySerial(16, 17); // RX, TX
void setup() {
  Serial.begin(115200);
  mySerial.begin(9600);
}
void loop() {
  if(mySerial.available() > 0){
    delay(4);
    if(mySerial.read() == 0xff){    //Judge packet header
      buffer_RTT[0] = 0xff;
      for (int i=1; i<4; i++){
        buffer_RTT[i] = mySerial.read();    //Read data
      }
      CS = buffer_RTT[0] + buffer_RTT[1]+ buffer_RTT[2];  //Compute checksum
      if(buffer_RTT[3] == CS) {
        Distance = (buffer_RTT[1] << 8) + buffer_RTT[2];//Calculate distance
        Serial.print("Distance:");
        Serial.print(Distance);
        Serial.println("mm");
      }
    }
  }
}


