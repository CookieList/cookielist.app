$.state.__admin_editor = null;
$.state.__admin_option_yaml_mapping = {};

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

ADMIN_OPTIONS = [
  {
    route: "/ping",
    description: "Ping Server",
    yaml:
      "# Method 'GET'\n" +
      "# This is a test to check if the server is up and running.\n",
  },
  {
    route: "/about_system_statistics",
    description: "System Statistics",
    yaml:
      "# Method 'GET'\n" +
      "# This will return the statistics of the system on which server is running.\n",
  },
  {
    route: "/access_debug_mode",
    description: "Set Debug Mode Password",
    yaml:
      "# Method 'GET'\n" +
      "# This will set the password for debug mode in current session.\n" +
      "\n" +
      "# Method 'POST'\n" +
      "# This will check password.\n" +
      "\n" +
      'password: "<NEW_PASSWORD>"\n' +
      "\n" + 
      "# Method 'DELETE'\n" +
      "# This will remove the password for debug mode in current session.\n",
  },
];

function InitializeAdminSystem() {
  $.state.__admin_editor = ace.edit($.id("[container]-admin.editor").get(0));
  $.state.__admin_editor.setTheme("ace/theme/one_dark");
  $.state.__admin_editor.session.setMode("ace/mode/yaml");
  $.state.__admin_editor.setShowPrintMargin(false);

  var servers = [window.location.host];
  servers.push(...$.state.cookielist.BADGE_SERVERS);
  const server_selection = $.id("[container]-admin.servers");
  $.each(servers, (index, server) => {
    server_selection.append(
      $("<option></option>")
        .attr("value", window.location.protocol + "//" + server + "/_")
        .text(server)
    );
  });

  const option_selection = $.id("[container]-admin.options");
  $.each(ADMIN_OPTIONS, (index, option) => {
    $.state.__admin_option_yaml_mapping[option.route] = option.yaml.trim();
    option_selection.append(
      $("<option></option>")
        .attr("value", option.route)
        .text("Preset: " + option.description)
    );
  });

  option_selection.on("change", () => {
    const route = option_selection.val();
    const yaml = $.state.__admin_option_yaml_mapping[route];
    $.id("[container]-admin.route").val(route);
    $.state.__admin_editor.setValue(yaml, -1);
    $.storage("__last_select_admin_option", route);
  });

  option_selection
    .val(
      $.storage("__last_select_admin_option")
        ? $.storage("__last_select_admin_option")
        : ADMIN_OPTIONS[0].route
    )
    .trigger("change");
}

function AdminContentFetch(method) {
  var __allowed = true;
  var URL = $.id("[container]-admin.servers").val();
  const route = $.id("[container]-admin.route").val().trim();
  if (route) {
    URL += route.startsWith("/") ? route : "/" + route;
  } else {
    $.notification("failed", "Route can't be empty");
    return;
  }
  var parameters = {};
  try {
    var yaml = $.state.__admin_editor.getValue().trim();
    if (yaml) {
      parameters = jsyaml.load(yaml, {
        schema: jsyaml.JSON_SCHEMA,
        json: true,
      });
    }
  } catch (error) {
    $.notification("failed", "Invalid YAML data");
    return;
  }
  if (method === "GET") {
    if (!route.includes("?")) {
      URL += "?";
    } else {
      if (!route.endsWith("&")) {
        URL += "&";
      }
    }
    URL += $.param(parameters);
  }

  const output = $.id("[container]-admin@response");
  output.html($.id("[container]-admin@template.loading").html());
  $.cookielist(
    URL,
    method === "GET" ? {} : parameters,
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
    (jqXHR) => {
      output.mustache($.id("[container]-admin@template.admin_api_error"), {
        status: jqXHR.status,
      });
    },
    method
  );
}
