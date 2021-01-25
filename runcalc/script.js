/* If you're feeling fancy you can add interactivity 
    to your site with Javascript */

String.prototype.parseTotalSeconds = function() {
  var parts = input.innerText.split(":");
    var hours = 0;
    var minutes = 0;
    var seconds = 0;

    if (parts.length == 1) {
      minutes = parseFloat(parts[0]);
    } else if (parts.length == 2) {
      minutes = parseFloat(parts[0]);
      seconds = parseFloat(parts[1]);
    } else if (parts.length == 3) {
      hours = parseFloat(parts[0]);
      minutes = parseFloat(parts[1]);
      seconds = parseFloat(parts[2]);
    } else {
      return 0;
    }

    return seconds + (minutes * 60) + (hours * 60 * 60);
}

String.prototype.toHHMMSS = function() {
  var sec_num = parseInt(this, 10); // don't forget the second param
  var hours = Math.floor(sec_num / 3600);
  var minutes = Math.floor((sec_num - hours * 3600) / 60);
  var seconds = sec_num - hours * 3600 - minutes * 60;

  if (hours < 10) {
    hours = "0" + hours;
  }
  if (minutes < 10) {
    minutes = "0" + minutes;
  }
  if (seconds < 10) {
    seconds = "0" + seconds;
  }
  if (hours != "00") {
    return hours + ":" + minutes + ":" + seconds;
  }
  return minutes + ":" + seconds;
};

var input = document.getElementById("input");
var mode = "pace";

function addResult(r) {
  var results = document.querySelector("#results");
  var el = document.createElement("li");
  el.innerText = r;
  results.appendChild(el);
}

document.body.onclick = e => {
  // input buttons
  if (e.target.dataset.in) {
    let val = e.target.dataset.in;

    // can only have a single "."
    if (val == ".") {
      if (mode == "dist" && input.innerText.indexOf(".") == -1) {
        input.innerText = input.innerText + val;
      }
      return;
    }

    // can only have a single ":"
    if (val == ":") {
      if (mode == "pace" && input.innerText.indexOf(":") == -1) {
        input.innerText = input.innerText + val;
      }

      return;
    }

    // clear the input if it's just "0"
    if (input.innerText === "0") {
      input.innerText = "";
    }

    input.innerText = input.innerText + val;
  }

  // special buttons
  if (e.target.dataset.special || e.target.tagName == "svg") {
    if (e.target.dataset.special == "clear") {
      input.innerText = "0";
    }
    
    if (e.target.dataset.special == "backspace" || (e.target.tagName == "svg")) {
      input.innerText = input.innerText.slice(0, input.innerText.length - 1);
      if (input.innerText.length == 0) {
        input.innerText = "0";
      }
    }
  }

  // conversions
  if (e.target.dataset.convert) {
    var total_seconds = input.innerText.parseTotalSeconds();

    if (e.target.dataset.convert == "mins/mi") {
      addResult(
        (total_seconds + "").toHHMMSS() +
          " mins/km == " +
          ((total_seconds * 1.609344) + "").toHHMMSS() +
          " mins/mi"
      );
    }
    
    if (e.target.dataset.convert == "mins/km") {
      addResult(
        (total_seconds + "").toHHMMSS() +
          " mins/mi == " +
          ((total_seconds / 1.609344) + "").toHHMMSS() +
          " mins/km"
      );
    }
    if (e.target.dataset.convert == "km/h") {
      var km_h = 60 / (total_seconds / 60);
      addResult((total_seconds + "").toHHMMSS() + " mins/km == " + km_h.toFixed(2) + " km/h");
    }    
  }

  // distance buttons
  if (e.target.dataset.distance) {
    var metric = document.querySelector("#mode").innerText.indexOf("Metric") > -1;

    var dist = parseFloat(e.target.dataset.distance);
    var seconds;

    if (input.innerText.indexOf(":") > -1) {
      var parts = input.innerText.split(":");
      var mins = parseFloat(parts[0]);
      seconds = parseFloat(parts[1]);
      seconds += mins * 60;
    } else {
      seconds = parseFloat(input.innerText) * 60;
    }
    
    if (document.querySelector("#mode").innerText.indexOf("Pace") > -1) {
      var result = seconds * (dist / 1000);

      if (!metric) {
        result = result / 1.609;
      }

      if (seconds > 0) {
        addResult(
          (seconds + "").toHHMMSS() +
            (metric ? " mins/km == " : " mins/mi == ")+
            (result + "").toHHMMSS() +
            " " +
            e.target.innerText
        );
      }      
    }
  }
  
  // input mode switch
  if (e.target.id == "mode") {
    var metric = document.querySelector("#mode").innerText.indexOf("Metric") > -1;
    if (metric) {
      e.target.innerText = "Imperial Pace";
    } else {
      e.target.innerText = "Metric Pace";
    }
  }
};
