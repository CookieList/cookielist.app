function SharePage(Site) {
  const share = window.location.origin + window.location.pathname
  if (Site === "_COPY") {
    ClipboardJS.copy(share);
    $.notification("tell", "URL Copied To Clipboard");
  } else {
    $.popup(Site + encodeURIComponent(share));
  }
}
