---
description: "Live 3DStep pages with fewer controls: the view with its step buttons only, the view alone, and one embed per instruction with ?step=N&controls=none."
hide:
  - toc
---
# Controls and steps

The same page can be embedded with less around the view. These embeds all load [the PiCAN 2 example](assembly.md), with a parameter added to its address.

## The view and its step buttons

`?controls=minimal` leaves out the step panel. The step counter and the Previous, Play all and Next buttons sit over the view, and the step's title under it:

```markdown
![Put the PiCAN 2 in its shell](../../3d/pican2/pican2.3dstep.html?controls=minimal){ type=iframe }
```

![Put the PiCAN 2 in its shell, with the step buttons over the view](../../3d/pican2/pican2.3dstep.html?controls=minimal){ type=iframe }

## One view per instruction

`?step=N&controls=none` shows one step of the page and nothing but its view, which the reader can still turn. Embedded once per instruction, it puts the model beside your own text, in the order and the words of your page:

```markdown
1. Turn the top shell over, then lay the PiCAN 2 board in it, components first.

    ![Step 1: the board over the upturned top shell](../../3d/pican2/pican2.3dstep.html?step=1&controls=none){ type=iframe }
```

1. Turn the top shell over, then lay the PiCAN 2 board in it, components first. The XH connector goes through the notch at one end, and the USB plug sticks out of the other.

    ![Step 1: the board over the upturned top shell](../../3d/pican2/pican2.3dstep.html?step=1&controls=none){ type=iframe }

2. Slide the board toward the USB end as far as it goes.

    ![Step 2: the board pushed toward the USB end](../../3d/pican2/pican2.3dstep.html?step=2&controls=none){ type=iframe }

3. Fit the lip at the XH connector end of the bottom shell first, then press the USB end down until the shell snaps shut.

    ![Step 3: the bottom shell over the board, lip end first](../../3d/pican2/pican2.3dstep.html?step=3&controls=none){ type=iframe }

Each embed is the whole page, models included, so a page of embeds loads one copy per embed. md-iframe loads each one only when it comes into view, and a viewer draws nothing while it is out of sight, so the embeds further down cost nothing until the reader gets there. `?step=` also takes a step's `id`: `?step=bottom` is the third step here.

## For every embed of a theme

A theme sets the same for every page that uses it, with [`controls`](../reference/themes.md#behavior) in its `[behavior]` table. A parameter in the address wins over the theme. [The generated page](../reference/page.md#url-parameters) lists every parameter.
