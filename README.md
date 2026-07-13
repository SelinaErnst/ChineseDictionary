# ChineseDictionary (ChD) <img src="appdata/images/book_icon.png" align="right"  width="90">

This application is capable of storing chinese vocabulary and grammar rules. The goal is to be able to personally note down information for newly learned chinese characters and link them to related grammar rules. Character Images (in SVG format) can also be uploaded.

Another aspect is the compatibility of the ChD dictionaries with one very popular dictionary for Mandarin and Cantonese learners, called [Pleco](https://www.pleco.com/)
. This app, available only for android and iOS, makes the creation of a personalized dictionary possible. By exporting a personal dictionary from ChD, a txt file is created which can then be imported by Pleco.

Since Pleco is only available for android and iOS, the advantage of ChD is, that you can run the python script on Windows and Linux, while the apk file can be run on android. It is possible to share dictionary information among each device by using backup and restore.  

## Table of Contents

- [ChineseDictionary (ChD) ](#chinesedictionary-chd-)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Build Application](#build-application)
    - [First Steps (APK)](#first-steps-apk)
  - [Templates](#templates)
      - [Pleco syntax in txt form:](#pleco-syntax-in-txt-form)
      - [How it is presented in the ChD and in the Pleco app:](#how-it-is-presented-in-the-chd-and-in-the-pleco-app)
      - [template:](#template)
  - [Demonstration](#demonstration)
    - [Character Dictionary](#character-dictionary)
    - [Grammar Dictionary](#grammar-dictionary)
    - [Settings](#settings)
  - [Pleco Compatibility](#pleco-compatibility)

## Installation

### Requirements
To be able to run the main.py, the following packages have to be installed.

```python
pip install kivy==2.3.1
pip install https://github.com/kivymd/KivyMD/archive/master.zip  # kivymd (Version: 2.0.1.dev0)
pip install materialyoucolor==2.0.10
```
### Build Application
Buildozer is used to create the .apk for android devices. The buildozer.spec specifies how the application will be compiled. Inside the Workspace, run these commands to build the application.

```python
buildozer -v android debug # builds the debug APK
buildozer android release # builds AAB for public distribution  
```

### First Steps (APK)

Before doing anything, the access to storage has to be granted. This is because all the information on characters and grammar will be stored locally. The next step is to determine where these files will be stored (app directory). This can be changed in the settings.

<div style="display: flex; gap: 10px;">
  <img src="appdata/documentation/Screenshot_20260713-212519.png" width="30%">
  <img src="appdata/documentation/Screenshot_20260713-212559.png" width="30%">
  <img src="appdata/documentation/Screenshot_20260713-213250.png" width="30%">
</div>

## Templates

Templates are used to convert entries into txt files that are compatible with the Pleco app. This step involves understanding Pleco syntax. It has been said, that the syntax one can use to beautify personalized dictionaries in Pleco is not meant for public usage. That is the reason why that exact syntax is quite difficult to use. The following text includes commands for color, font style and positioning of text. The idea behind using a template is that each command which is unreadable in the Pleco syntax will be clearly stated and can be easily changed. 

#### Pleco syntax in txt form:
> 水[]	shui3	1A0AENG ◼ water ◼ body of water (river, lake, etc.) ◼ liquid ◼ floodGER ◼ Wasser ◼ Gewässer ◼ FlüssigkeitMW ◼ washings, rinsings (of a garment)RAD ◼ KangXi 85: waterOPP ◼ 冰 [bīng] ◼ 水蒸汽 [shuǐzhēngqì]INFORMATION1A0PVARIANTS: 氵 · 氺CHARACTER1A0PSTROKES: (4)񄪱 񄪲 񄪳 񄪴MNEMONICS: ◼ kneeling by a stream of waterMEANING AS COMPONENT: ◼ liquid ◼ actions involving liquids (like pouring, flowing, swimming, etc)ORIGINS: 水 depicts flowing water. As a component, it is more often written 氵or 氺.ANCIENT FORM: AA10񁠨OCCURENCES1A0PRELATIVES: 冰 [bīng] A0PAA00https://zi.tools/zi/水

#### How it is presented in the ChD and in the Pleco app:
<div style="display: flex; gap: 10px;">
  <img src="appdata/documentation/Screenshot_20260713-224745.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224749.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224900.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224905.png" width="19%">
</div>

#### template:
```
<H:[b|grey|hidden]:TRANSLATION>
<LEFT>{
<H:[nb|blue|available]:ENG ><L:[point|l|normal]:english><E>
<H:[nb|blue|available]:GER ><L:[point|l|normal]:german><E>
<H:[nb|teal|available]:MW ><L:[point|l|normal]:measure_word><E>
<H:[nb|teal|available]:RAD ><L:[point|l|normal]:radical><E>
<H:[nb|green|available]:OPP ><L:[point|l|normal]:opposite><E>
}<E>
<H:[b|grey|available]:INFORMATION>
<INDENT>{
<H:[nb|grey|available]:CLASSIFIER: ><L:[dot|l|normal]:classifier><E>
<H:[nb|grey|available]:VARIANTS: ><L:[dot|l|normal]:variants><E>
<H:[nb|grey|available]:DISTINGUISH FROM: ><L:[dot|l|normal]:others><E>
<H:[nb|grey|available]:DICTIONARY ENTRIES: ><N><L_LINK:[dot|l|normal]:dict_entries><E>
}<E>
<H:[b|grey|available]:CHARACTER>
<INDENT>{
<H:[nb|grey|available]:STROKES: ><(><I:[n|none|normal]:strokes_count><)><T:[n|none|normal]:strokes><E>
<H:[nb|grey|available]:COMPONENTS: ><N><L:[point|nl|normal]:components><E>
<H:[nb|grey|available]:MNEMONICS: ><L:[point|l|normal]:mnemonics><E>
<H:[nb|grey|available]:MEANING AS COMPONENT: ><L:[point|l|normal]:usage><E>
<H:[nb|grey|available]:ORIGINS: ><T:[n|none|normal]:origin><E>
<H:[nb|grey|available]:ANCIENT FORM: ><L:[none|l|big]:ancient><E>
}<E>
<H:[b|grey|available]:OCCURENCES>
<INDENT>{
<H:[nb|grey|available]:RELATIVES: ><L:[dot|l|normal]:relatives><E>
<H:[nb|grey|available]:WORDS: ><L:[dot|l|normal]:words><E>
}<E>
<H:[b|grey|hidden]:LINKS>
<RIGHT>{
<L_LINK:[none|nl|small]:link><E>
}<E>
```
Each template can contain multiple components and environments. A component is either a header (H) or content, which can be a list (L), an integer number (I) or plain text (T). An environment can position the text on the left, right or with an indent. The environment always is started by a header.

```
Header description: <H:[font|color|visibility]:TEXT>
Content description: <L:[delimiter|newline|size]:category> 
Environment description: <H:[font|color|visibility]:TEXT><position>{...}<E>

End of line: <E>
additonal character: <(> or <)>
```

Headers have an interesting function, where based on what visibility they are described to have and based on whether or not the character entry has information for that category, the header and the following content might not be presented. This is necessary because otherwise every information category would be visible for every character / dictionary entry even when most of that information is missing or not available. To keep things easy and simple, only those categories that have information input are shown in the Pleco App. 

## Demonstration

### Character Dictionary

ChD allows the creation of multiple dictionaries. This can be helpful to separate one-character symbols from words or any other distinction that might be necessary. The dictionary can be sorted, filtered and searched through.  
In the preview of each character, the chinese character symbols are shown and a part of the english translation. When available, the character image is shown on the side. There you also find category symbols that can be filtered for. 

Filter:
 - translated character (any character that has a translation)
 - radical (any character that is considered a radical, has information about the radical)
 - measure word (a character that is used as a measure word in the chinese language)
 - grammatical (in case the character is relevant to a grammatical rule)

<div style="display: flex; gap: 10px;">
  <img src="appdata/documentation/Screenshot_20260713-211254.png" width="30%">
  <img src="appdata/documentation/Screenshot_20260713-211325.png" width="30%">
  <img src="appdata/documentation/Screenshot_20260713-213552.png" width="30%">
</div>

### Grammar Dictionary

There is only one list of grammar rules. Each rule should be allocated to a certain learning level. Shown here are the rules for level A1. When no level is selected, only rules without a level would be selected. When searching for a grammar rule, text from the title, subtitle and tags can be used. 

<div style="display: flex; gap: 10px;">
  <img src="appdata/documentation/Screenshot_20260713-214654.png" width="30%">
  <img src="appdata/documentation/Screenshot_20260713-214724.png" width="30%">
  <img src="appdata/documentation/Screenshot_20260713-214753.png" width="30%">
</div>

### Settings

The theme and design palette can be changed through settings. Changes here will be saved to a settings.json file in .config of the app directory.

<div style="display: flex; gap: 10px;">
  <img src="appdata/documentation/Screenshot_20260713-220003.png" width="30%">
  <img src="appdata/documentation/Screenshot_20260713-220009.png" width="30%">
  <img src="appdata/documentation/Screenshot_20260713-220117.png" width="30%">
</div>

## Pleco Compatibility

Based on templates that were created to determine font style and other design choices, the information stored for the characters in a dictionary or even a grammar rule is converted to a txt file using Pleco specific syntax. 

This is how a character entry looks in ChD and in Pleco.
<div style="display: flex; gap: 10px;">
  <img src="appdata/documentation/Screenshot_20260713-224745.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224749.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224900.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224905.png" width="19%">
</div>

\
This is how a grammar entry looks in ChD and in Pleco.

<div style="display: flex; gap: 10px;">
  <img src="appdata/documentation/Screenshot_20260713-224631.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224642.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224517.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224538.png" width="19%">
  <img src="appdata/documentation/Screenshot_20260713-224550.png" width="19%">
</div>
