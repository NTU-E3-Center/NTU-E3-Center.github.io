# The Assets

Here are the assets used in the website. The folder/files, its functions, and how it works are listed below.

## modules
Modules to make your life easier.

### Modules:
#### 1. [compress-img](/assets/modules/compress-img.py)

Compress image files into several sizes of the file, to have better performance.

#### 2. [g-scholar-scrape](/assets/modules/g-scholar-scrape.py)
Scrape the publication (usually only journal publications) information from the Google Scholar page of I-Yun Lisa Hsieh, including `citationId`, `title`, `link`, `journal`, `volume`, `year`, `month`.

However, it only add the newest publications that were not in the file,for example:

The following publications were in the original file: A, B, E, F (A is oldest, F is newest, D was removed manually)
Now, there were new publications C, G, H, the module will only add G, H into the file, all the older publications that wanted to be added, manually type in is required.

Noted that the title ij the section is named 'Journal Publications', so other forms of publications should be avoided.

## src
Sources to render our beautiful web page.

### abt.json

### mem.json
The member's information.
Please modify it with the same structure within the file.
There are 4 types of roles: `professor`, `assistant`, `doctor`, `master`, please add information in order.
The orders in the file will directly affect the order shown on the website, it usually lists the member from the oldest to newest.

### res.json

### pub.json

### new.json

### glf.json

---

## mem
The photos in the #members section.

### Instructions:
1. Simply put the original image file in this folder.
2. Modify the [src/mem.json](/assets/src/mem.json) file.
3. The [compress-img](/assets/modules/compress-img.py) module will do the rest for you.

## new
The photos/files in the #news section.

Instructions:
1. Simply put the original file in this folder.
2. Modify the [src/new.json](/assets/src/new.json) file.

## glf
The photos in the #group-life section.

Instructions:
1. Simply put the original image file in this folder.
2. Modify the [src/glf.json](/assets/src/glf.json) file.
3. The [compress-img](/assets/modules/compress-img.py) module will do the rest for you.
