# _Project_Design_2_
Something can do vision test at home

## Features and Details
<details open>
<summary>User Interface</summary>

- White screen area 
  - C letter size and direction
- Correct or wrong  
- Time limit
- Vision test result
</details>
<details open>
<summary>Backend process</summary>
  
- Estimate the distance between user and camera before test
  - Still discussion
- Pose detection
  - Detect user's finger pointing or palm swinging direction  
- Vision test mechanism
  1. Generate time limit, C letter information
  2. Judge answer
  3. Record and calculate
</details>

## Tools and APIs
| Works | Methods |
| ----- | ------ |
| Pose detection  | Openpose, Opencv  |
| User Interface  | PyQt5  |

## Others
Webcam first, try to move project to Android or IOS

使用指令安裝套件:pip install -r requirements.txt