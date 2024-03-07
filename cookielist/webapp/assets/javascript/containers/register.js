function RegisterUser() {
  const token = getToken();
  if (token) {
    $.cookielist(
      $.state.endpoints.register,
      { token: token, action: "login" },
      (response) => {
        if (response.status === "success") {
          const url = $.storage("__URL");
          $.storage("__URL", null);
          $.storage("__FLASH_MODE", "success");
          $.storage("__FLASH_MESSAGE", "AniList Login Successful");
          if (url) {
            window.location.replace(url);
          } else {
            window.location.replace($.state.endpoints.index);
          }
        } else {
          $.storage("__FLASH_MODE", "failed");
          $.storage("__FLASH_MESSAGE", "AniList Login Failed");
          window.location.replace($.state.endpoints.index);
        }
      }
    );
  } else {
    $.id("[_]-register.success").addClass("!hidden");
    $.id("[_]-register.failed").addClass("!flex");
  }
}

function getToken() {
  if (window.location.hash) {
    try {
      return window.location.hash
        .substring(1)
        .split("access_token=")[1]
        .split("&token_type")[0]
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/>/g, "&gt;");
    } catch {
      return null;
    }
  } else {
    return null;
  }
}
