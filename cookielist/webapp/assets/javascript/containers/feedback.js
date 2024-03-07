function sendFeedback(Feedback) {
  $.id("[container]-feedback.feedback_send_button").addClass(
    "hover:!bg-gray-100 !cursor-not-allowed dark:hover:!bg-slate-800"
  );
  $.id("[container]-feedback.feedback_send_button").html(
    $.id("[container]-feedback@template.msg_sending").html()
  );
  $.anilist(
    $.state.graphql.feedback,
    {
      recipient: Number($.state.cookielist.ANILIST_DEV_ID),
      message: $.mustache(
        $.id("[container]-feedback@template.anilist_message_template"),
        {
          origin: window.location.origin,
          message: Feedback,
          pageUser: {
            name: $.state.page.name,
            id: $.state.page.id,
          },
          currentUser: {
            name: $.state.session.name,
            id: $.state.session.id,
          },
        }
      ),
    },
    (response) => {
      $.id("[container]-feedback.feedback_send_button").removeClass(
        "hover:!bg-gray-100 !cursor-not-allowed dark:hover:!bg-slate-800"
      );
      $.id("[container]-feedback.feedback_send_button").html(
        $.id("[container]-feedback@template.msg_sent").html()
      );
      $.id("[container]-feedback.message_returned_badge").append(
        $.mustache(
          $.id("[container]-feedback@template.feedback_sent_success_message"),
          {
            url: response.data.SaveMessageActivity.siteUrl,
          }
        )
      );
      if ($.storage("__FEEDBACK")) {
        $.storage(
          "__FEEDBACK",
          $.storage("__FEEDBACK")
            .split(",")
            .concat(String(response.data.SaveMessageActivity.id))
            .join(",")
        );
      } else {
        $.storage("__FEEDBACK", String(response.data.SaveMessageActivity.id));
      }
      updatePreviousFeedbacks();
      $.storage("__FEEDBACK_MESSAGE", null);
      $.id("[container]-feedback.feedback_box").val("");
      $.notification("success", "Feedback Sent");
    }
  );
}

function updatePreviousFeedbacks() {
  if ($.storage("__FEEDBACK")) {
    $.id("[container]-feedback.feedback_history")
      .addClass("flex flex-col")
      .removeClass("hidden");
    $.id("[container]-feedback.feedback_history.history_container").mustache(
      $.id("[container]-feedback@template.sent_feedbacks"),
      { ids: $.storage("__FEEDBACK").split(",") }
    );
  } else {
    $.id("[container]-feedback.feedback_history").addClass("hidden");
  }
}

function clearFeedbacks() {
  $.storage("__FEEDBACK", null);
  updatePreviousFeedbacks();
}

function InitializeFeedbackSystem() {
  updatePreviousFeedbacks();
  if ($.state.session.token) {
    const feedback_box = $.id("[container]-feedback.feedback_box");
    feedback_box.val($.storage("__FEEDBACK_MESSAGE"));
    $.id("[container]-feedback.feedback_send_button").click(() => {
      const feedback = feedback_box.val().trim();
      if (feedback) {
        sendFeedback(feedback);
      } else {
        $.notification("failed", "Feedback Cant Be Empty");
      }
    });
    feedback_box.keyup(() => {
      $.storage("__FEEDBACK_MESSAGE", feedback_box.val());
    });
  } else {
    $.id("[container]-feedback.feedback_send_button").addClass(
      "hover:!bg-gray-100 !cursor-not-allowed dark:hover:!bg-slate-800"
    );
    $.id(
      "[container]-feedback.message_returned_badge.not_logged_in"
    ).removeClass("hidden");
  }
}
