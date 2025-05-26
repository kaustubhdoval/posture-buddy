<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
<h3 align="center">Posture Buddy</h3>

  <p align="center">
    Real Time Posture Analysis using OpenCV and MediaPipe
    <br />
    <a href="https://github.com/kaustubhdoval/posture-buddy"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/kaustubhdoval/posture-buddy/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/kaustubhdoval/posture-buddy/issues">Request Feature</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project
Python Script to provide Real Time Posture Analysis using OpenCV and MediaPipe. Learn more at my [Website](https://kdoval.com/projects/posture-buddy)
<br/> <br/>
<em> For V1: </em> Currently the program only detects BAD/GOOD posture, if Posture is BAD for over a particular time (7 seconds by default) a function called ```sendWarning()``` is called. The condition of posture is determined by evaluating two angles - the neck-shoulder and torso-shoulder angles. 
<br/> <br/>
I made the project to receieve a TCP Stream from a Raspberry Pi with a camera module. If you want to do the same you can run this script on your RPi: 
```sh
libcamera-vid -t 0 --width 640 --height 480 --framerate 12 --codec h264 -o - | ffmpeg -i - -c:v copy -f mpegts -listen_timeout 10000 tcp://<RASPBERRY_IP>:5000?listen
```
The camera stream does not need to be particularly high quality, just ensure that there is enough adequate lighting to assist the CV Models to perform the best they can. 

### Built With
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![Mediapipe](https://img.shields.io/badge/mediapipe-0097A7.svg?style=for-the-badge&logo=mediapipe&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi)





<!-- CONTACT -->
## Contact

Kaustubh Doval - kaustubhdoval@gmail.com

<p align="right">(<a href="#readme-top">back to top</a>)</p>


[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
