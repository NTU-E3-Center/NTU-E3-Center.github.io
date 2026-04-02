# Where magic is held

## `page.json`
---
All of the pages and inner pages are structured in this file.

For the main page (`index.html`), section listing feature is provided. you can swap each section with others to change up the page structure.

Since there are no videos now, the `video` section has been marked out. If you like to place it on page, simply remove `_` from the items of `video`.

## `videos.json`
---
Two kinds of video source is accepted:
### 1. Local Videos

Simply put the video file and a thumbnail image file in `/contents/video/` then structure as following:
```
{
    "mediaType": "local",
    "videoPath": "/assets/videos/2025-1.mp4",
    "imgPath": "/assets/videos/2025-1.jpg",
    "description": "Nice local video.",
    "year": "'25",
    "month": "Sep."
}
```
*If no `imgPath` is coded, there will be a blank white block.*

---

### 2. Youtube Videos
For Youtube videos, simply copy the source ID from the Youtube video link.

e.g. `https://www.youtube.com/watch?v=dQw4w9WgXcQ` take the string behind `?v=`, that is, `dQw4w9WgXcQ`.

then structure as following:

```
{
    "mediaType": "youtube",
    "ytSourceId": "lqROCM7BVSA",
    "imgPath": "/assets/group-life/2025-3.jpg",
    "description": "Nice Youtube video.",
    "year": "'25",
    "month": "Sep."
}
```

*You can manually add an thumbnail image by stating `imgPath`, however, if no `imgPath` is passed, it will automatically fetch the thumbnail image from that exact video by the following way:
`https://img.youtube.com/vi/{{item['ytSourceId']}}/hqdefault.jpg`*

