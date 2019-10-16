# Mol-sys-stand
Molecular Systems Game featuring Henning. Originally made in PyGame by Daniel Rice 

1. Set up the scales - attach hx711 to Raspberry Pi and scales as shown here 
(https://www.instructables.com/id/Arduino-Bathroom-Scale-With-50-Kg-Load-Cells-and-H/) with:
    Scale left to pins 5 and 6 of Raspberry Pi
    Scale right to pins 23 and 24 of Raspberry Pi
    
2. Set up the stand - Make sure the scales left and right are in the correct position and add the blood vessels (buckets).  

3. Calibrate - Warm up the scales by adding and removing weights to the buckets a few times. On the Raspberry Pi there is a HX711
folder containing an example file for calibrating the scales. Run the "example" script to calibrate each scale individually. Have
something of a known weight, make sure you've chosen the correct pins at the top of the program, and follow the instructions in the
program file/script output; it will tell you what to do. This will generate a number called the reference unit. 

4. Game set up - Open the game script and add the reference unit for each scale in the following lines of the script: 

      scale_left = Scale(5, 6, -22.5)
      
      scale_right = Scale(23, 24, -25.7)

    In this example the reference unit is -22.5 for the left scale and -25.7 for the right scale. Note that it also defines the
    pins of the scales. Now the scales should be reading as zero when there is nothing in the bucket. 

5. Run the game
    
