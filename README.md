# light_rendering
Rendering light propagation in 2D plane in Python

! The project is probably not optimized perfectly, and written 100% professionally, please bear with me as I'm still learning :)

## Render v2.0
[render v2.py](render%20v2.py)

Works with color lights

![](Renders/Render_v2%20(600,%20600)%2027-04%2018-03%20.png)

![](Renders/Render_v2%20(800,%20800)%2026-04%2015-08%20.png)

![](Renders/Render_v2%20(400,%20400)%2026-04%2013-26%20.png)

Because of perfect smoothness of this v2.0 rendering, I added a small noise

```python
intensity = (len(samples)/90) + (random.random()/20)
```

With noise

![](Renders/Render_v2%20(400,%20400)%2017-04%2015-28%20.png)

Without noise

![](Renders/Render_v2%20(400,%20400)%2016-04%2018-24%20.png)

## Render v1.0
[render.py](render.py)

v1.0 rendering in comparision to v2.0, casted rays all around which resulted in calculating many intersection of rays, that weren't possible to meet with any light source.
In v2.0 I changed algorithm to find areas in which we calculate only rays that can possibly intersect with a light source, which lead to much less calculations and more accurate results.

The same render from above made with v1.0 rendering

![](Renders/Render%20(400,%20400,%20360,%202)%2014-04%2013-16%20.png)

That's why in terms of v1.0 rendering, we could set an accuracy of result -> more rays = more accurate result

144 rays per pixel

![](Renders/Render%20(400,%20400,%20144,%202)%2011-04%2008-30.png)

36 rays per pixel

![](Renders/Render%20(400,%20400,%2036,%202)%2011-04%2010-44%20.png)
