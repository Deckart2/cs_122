<!--
*** Thanks for checking out this README Template. If you have a suggestion that would
*** make this better, please fork the repo and create a pull request or simply open
*** an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo, twitter_handle, email
-->
<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a>
    <img src="static_img/twitter_2.png" alt="Logo" width="110" height="80">
  </a>

  <h3 align="center">Analysis of Tweets & Voting Behavior of Congressmen on the #StopTheSteal movement</h3>

<!-- TABLE OF CONTENTS -->
## Table of Contents

- [Table of Contents](#table-of-contents)
- [About The Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

<!-- ABOUT THE PROJECT -->
## About The Project

On January 6th, 2021, violent insurrectionists stormed the US Capitol. Congress members were forced to halt their ratification of the 2020 election results and flee for safety. This riot was the culmination of President Donald Trump’s efforts to delegitimize the election, and the result of President Trump and his supporters’ political disinformation “stopthesteal” campaign.
 
From the November election up to the insurrection, speech from constituents and their representatives became increasingly polarized and inflammatory. We have analyzed two primary topics during this period of civil unrest. First, to what extent were Congressional Representatives’ speech, measured by their tweets between November 7th, 2020 and January 6th 2021, reflective of their actual support of the campaign to overturn election results? Second, whether the Representatives’ tweets reflect those of their constituents. 
 
To assess these questions, we used the Twitter API to analyze each Representative’s tweets in the established timeframe by assessing common keywords and performing a sentiment analysis. We conducted similar analysis on constituent tweets that provide geographic data, allowing us to match accounts to Congressional Districts. Finally, we used Propublica’s API to assess how representatives voted on the ratification of the election results in Arizona and Pennsylvania, and the impeachment of President Trump. 

### Built With

* Bootstrap
* Flask
* Bokeh
* HTML/CSS
* Python

<!-- GETTING STARTED -->
## Getting Started
To get a local copy up and running follow these simple steps.

### Installation
 
1. Clone the repo
```sh
git clone repo-link
```
2. Navegate to the repo
```sh
cd ./cs_122
```
3. Install Environment
```sh
sh sudo bash ./install.sh
```
4. Activate project environment
```sh
source projenv/bin/activate
```
5. Run Program and Choose N (a later update may allow functionality if choosing Y)
```
sh sudo bash ./run_program.sh
```


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact
- Andres Crucetta - andres.crucetta@hey.com
- Jacob Lehr - jblehr@uchicago.edu
- Gabriel Morrison - gdmorrison@uchicago.edu
- Kelly Yang - kyy@uchicago.edu


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-url]: https://github.com/acrucetta/chicago_COVID_app/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/andres-crucetta/
[product-screenshot]: images/screenshot.png
