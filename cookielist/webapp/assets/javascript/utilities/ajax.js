function AjaxError(jqXHR, textStatus, errorThrown) {
  if (textStatus === "abort") {
    msg = "Ajax Request Aborted";
  } else if (jqXHR.status === 0) {
    msg = "Not Connected to Internet, Verify Network";
  } else if (jqXHR.status === 404) {
    msg = "Requested Page Not Found";
  } else if (jqXHR.status === 500) {
    msg = "Internal Server Error";
  } else if (textStatus === "parsererror") {
    msg = "Requested JSON Parse Failed";
  } else if (textStatus === "timeout") {
    msg = "Request Timed Out, Slow Internet Connection";
  } else if (jqXHR.status === 401) {
    msg = "Wrong API Token";
  } else if (jqXHR.status === 400) {
    msg = "Invalid GraphQL";
  } else {
    msg = "Something Went Wrong, Refresh Page";
  }
  $.notification("failed", msg);
}
