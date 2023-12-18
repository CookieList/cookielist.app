function openPopupWindow(url) {
  const width = 600;
  const height = 600;
  window.open(
    url,
    "_blank",
    [
      "location=yes",
      "popup=yes",
      "height=" + String(height),
      "width=" + String(width),
      "scrollbars=yes",
      "status=yes",
      "menubar=no",
      "toolbar=no",
      "resizable=yes",
      "left=" +
        String(
          window.screen.availLeft + window.screen.availWidth / 2 - width / 2
        ),
      "top=" +
        String(
          window.screen.availTop + window.screen.availHeight / 2 - height / 2
        ),
    ].join(",")
  );
}

function SharePage(Site) {
  const share = window.location.origin + window.location.pathname
  if (Site === "_COPY") {
    ClipboardJS.copy(share);
    $.notification("tell", "URL Copied To Clipboard");
  } else {
    openPopupWindow(Site + encodeURIComponent(share));
  }
}
