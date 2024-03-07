((clipboard) => {
  clipboard.on("success", function (element) {
    const active =
      "dark:!bg-emerald-600 dark:!text-emerald-900 dark:!hover:bg-emerald-700 !bg-green-200 !text-green-500 !hover:bg-white";
    const copyButton = $.id(element.trigger.id);
    copyButton.html(
      $.id("[container]-profile@template.copied_icon_svg").html()
    );
    copyButton.addClass(active);
    $.notification("tell", "Copied To Clipboard");
    setTimeout(() => {
      copyButton.removeClass(active);
      copyButton.html(
        $.id("[container]-profile@template.copy_icon_svg").html()
      );
    }, 900);

    element.clearSelection();
  });

  clipboard.on("error", function (e) {
    $.notification("failed", "Failed to copy, Please do it manually");
  });
})(new ClipboardJS("[cookie-badge]"));
