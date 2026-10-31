---
description: "The postMessage protocol an embedded page uses to tell md-iframe its content height, so the iframe grows and shrinks to fit."
---
# Auto-height protocol

An iframe does not size itself to its content. md-iframe fixes that with one small message: the embedded page posts its content height to the parent, and md-iframe sets the iframe to that height. This page describes the message, so any tool or hand-written page can take part.

PinConnect pinouts implement it today. The [live examples](../pinconnect/examples/index.md) on this site use it: narrow the window until a pinout's connector list moves below the board, and the frame grows to fit.

## The message

The embedded page posts a plain object to its parent window:

```js
parent.postMessage({ mdIframeHeight: 840 }, "*");
```

- **`mdIframeHeight`** is the height in CSS pixels that the iframe should have. Send a number, rounded up (`Math.ceil`).
- **A positive value** sets the iframe's `height` to that many pixels and drops its `min-height` floor, so the content alone decides the height and the frame can shrink as well as grow.
- **`0`** hands control back: the iframe returns to the `height` and `min-height` its tag was written with. Send it when the page no longer needs a custom height, such as a pinout whose layout went back to side by side on a wide screen.
- Values above 20000 are ignored, as are messages that are not objects or that carry no number.

md-iframe also accepts **`pinconnectHeight`** with the same meaning, the key that pinout-embed listened for. When a message carries both, `mdIframeHeight` wins.

## Which iframe it applies to

The listener matches the message's `event.source` against each md-iframe iframe's `contentWindow`, so several embeds on one page each get their own height, and the posting page does not need to know anything about where it is embedded. It does not check the origin: the only thing a message can do is set a height.

The listener is added once per page, only on pages that contain an md-iframe embed. It survives Material's and Zensical's instant navigation.

## Sending it

Report whenever the height can change: on load, on resize, and whenever your own layout changes. A `ResizeObserver` on `document.body` catches most of it. Skip repeats, so a parent that resizes the frame does not set off a loop:

```js
(function () {
  if (window.parent === window) return;      // not embedded
  var last = -1;
  function report() {
    var h = Math.ceil(document.body.scrollHeight);
    if (Math.abs(h - last) <= 2) return;     // ignore tiny or repeated changes
    last = h;
    parent.postMessage({ mdIframeHeight: h }, "*");
  }
  addEventListener("load", report);
  addEventListener("resize", report);
  if (window.ResizeObserver) new ResizeObserver(report).observe(document.body);
  report();
})();
```

Measure `document.body.scrollHeight`, not `document.documentElement.scrollHeight`: the root element is at least as tall as the viewport, which is the iframe itself, so a page measured that way could grow but never shrink.

While the parent sizes the frame to fit, the page's own scrollbar only gets in the way: it narrows the content, which changes the height, which brings the scrollbar back. Hide it (`document.documentElement.style.overflow = "hidden"`) while you report a positive height.

## Talking to older listeners

Sites that still run pinout-embed listen for `pinconnectHeight` alone. A page that should size itself on those sites too can send both keys in **one** message:

```js
parent.postMessage({ mdIframeHeight: h, pinconnectHeight: h }, "*");
```

This is what PinConnect pinouts send. Use a single message rather than two: md-iframe reads both keys, and two messages would set the height twice.

## What md-iframe does not do

- It never asks the page for its height. A page that never posts keeps its authored height, which is the right thing for a page that fills a fixed frame.
- It does not animate. If your page animates its own height, report it every frame; md-iframe sets each value as it arrives, and an iframe transition would only fight it.
- It does not reach into the page, so it works across origins. The [missing-file check](embedding.md#when-the-file-is-missing) is the one feature that needs the same origin.
