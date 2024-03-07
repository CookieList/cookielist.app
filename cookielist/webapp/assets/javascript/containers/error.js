function CopyException() {
  const exception = $("<textarea></textarea>")
    .html($.id("[exception]-text").html())
    .text();
  ClipboardJS.copy(exception);
  $.notification("tell", "Copied To Clipboard");
}

function CopyExceptionTrace() {
  const trace = $("<textarea></textarea>")
    .html($.id("[exception]-trace").html())
    .text();
  ClipboardJS.copy(trace);
  $.notification("tell", "Copied To Clipboard");
}

function ToggleExceptionWindow() {
  $.id("[exception]-details").toggleClass("hidden");
  $.id("[exception]-view").toggleClass("hidden");
}
