setInterval(update, 1000);

function update() {
  $.ajax({
    url: "../stats.json",
    success: function (json) {
      let nickname = document.getElementById("nickname");
      nickname.textContent = json["nickname"];
      let clear = document.getElementById("clear");
      clear.textContent = ("0" + json["clear"]).slice(-2) + "勝";
      let failure = document.getElementById("failure");
      failure.textContent = ("0" + json["failure"]).slice(-2) + "敗";
      let grade_point = document.getElementById("current-grade-point");
      grade_point.textContent =
        "評価" + ("000" + json["grade_point"]).slice(-3);

      const value =
        json["job_num"] == 0 ? 450 : (json["clear"] / json["job_num"]) * 900;
      let win = document.getElementById("background-win");
      win.setAttribute("width", value);
      let lose = document.getElementById("background-lose");
      lose.setAttribute("x", value);
      lose.setAttribute("width", 900 - value);
    },
  });
}
//   fetch("stats.json")
//     .then((response) => response.json())
//     .then((json) => {
//       let nickname = document.getElementById("nickname");
//       nickname.textContent = json["nickname"];
//       let clear = document.getElementById("clear");
//       clear.textContent = ("0" + json["clear"]).slice(-2) + "勝";
//       let failure = document.getElementById("failure");
//       failure.textContent = ("0" + json["failure"]).slice(-2) + "敗";
//       let grade_point = document.getElementById("current-grade-point");
//       grade_point.textContent =
//         "評価" + ("000" + json["grade_point"]).slice(-3);

//       const value =
//         json["job_num"] == 0 ? 450 : (json["clear"] / json["job_num"]) * 900;
//       let win = document.getElementById("background-win");
//       win.setAttribute("width", value);
//       let lose = document.getElementById("background-lose");
//       lose.setAttribute("x", value);
//       lose.setAttribute("width", 900 - value);
//     });
//   const date = new Date();
//   const hour = ("0" + date.getHours()).slice(-2);
//   const minutes = ("0" + date.getMinutes()).slice(-2);
//   const second = ("0" + date.getSeconds()).slice(-2);
//   const time = `${hour}:${minutes}:${second}`;
//   let current_time = document.getElementById("current-time");
//   current_time.textContent = time;
// }

function fetchLocal(url) {
  return new Promise(function (resolve, reject) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
      resolve(new Response(xhr.responseText, { status: xhr.status }));
    };
    xhr.onerror = function () {
      reject(new TypeError("Local request failed"));
    };
    xhr.open("GET", url);
    xhr.responseType = "arraybuffer";
    xhr.send(null);
  });
}
