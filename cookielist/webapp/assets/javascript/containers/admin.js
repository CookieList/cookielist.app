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

function AdminContentFetch(URL, ResponseId, method = "GET") {
  var __allowed = true;

  if (method !== "GET") {
    __allowed = confirm("POST:  " + window.location.origin + URL);
  }

  if (__allowed) {
    const output = $.id("[container]-admin@response." + ResponseId);
    output.html($.id("[container]-admin@template.loading").html());
    $.cookielist(
      window.location.origin + URL,
      {},
      (response) => {
        if (response.json) {
          response["json"] = hljs.highlight(
            JSON.stringify(response.json, null, "  "),
            { language: "json", ignoreIllegals: true }
          ).value;
        }
        if (response.markdown) {
          response["markdown"] = hljs.highlight(response.markdown, {
            language: "markdown",
            ignoreIllegals: true,
          }).value;
        }
        output.mustache(
          $.id("[container]-admin@template.admin_api_response"),
          response
        );
      },
      (method = method)
    );
  } else {
    $.notification('inform', 'Operation Canceled')
  }
}
