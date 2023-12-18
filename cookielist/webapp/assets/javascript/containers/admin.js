function AdminLogin() {
  const username = $.id("[container]-admin.username");
  const password = $.id("[container]-admin.password");
  const key = $.id("[container]-admin.key");
  const error = "!bg-rose-500/30 focus:!outline-rose-500/50";

  if (!username.val()) {
    $.notification("failed", "Username can't be empty");
    username.addClass(error);
  } else {
    username.removeClass(error);
    if (!password.val()) {
      $.notification("failed", "Password can't be empty");
      password.addClass(error);
    } else {
      password.removeClass(error);
      if (!key.val()) {
        $.notification("failed", "Key can't be empty");
        key.addClass(error);
      } else {
        key.removeClass(error);
      }
    }
  }

  if (username.val() && password.val() && key.val()) {
    $.cookielist(
      $.state.endpoints.register,
      {
        username: username.val(),
        password: password.val(),
        key: key.val(),
        action: "admin_login",
      },
      (result) => {
        if (result.status === "success") {
          $.notification("success", "You are now Logged in as Admin");
          $.refresh("show");
        } else {
          $.notification("failed", "Incorrect Credentials");
          username.val("");
          password.val("");
          key.val("");
        }
      }
    );
  }
}
