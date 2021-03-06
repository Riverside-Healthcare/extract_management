/*
    Extract Management 2.0
    Copyright (C) 2020  Riverside Healthcare, Kankakee, IL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

var ajaxContent = function () {
  function load(el, dest) {
    if (typeof dest == "undefined") {
      dest = el;
    }

    var q = new XMLHttpRequest();
    q.open("get", el.getAttribute("data-src"), true);
    q.send();

    q.onload = function () {
      el.innerHTML = this.responseText;

      // find and execute any javascript

      var js = Array.prototype.slice.call(
        el.querySelectorAll('script:not([type="application/json"])')
      );
      for (var x = 0; x < js.length; x++) {
        var q = document.createElement("script");
        q.innerHTML = js[x].innerHTML;
        q.type = "text/javascript";
        q.setAttribute("async", "true");
        el.appendChild(q);
        js[x].parentElement.removeChild(js[x]);
      }

      if (el.closest(".clps-o")) {
        el.closest(".clps-o").dispatchEvent(
          new Event("change", {
            bubbles: true,
          })
        );
      }
    };
  }

  var stuff = document.getElementsByClassName("em-ajaxContent");
  for (var x = 0; x < stuff.length; x++) {
    if (stuff[x].hasAttribute("data-src")) {
      load(stuff[x]);
    }
  }
};

ajaxContent();

(function () {
  document.addEventListener("click", function (e) {
    if (e.target.closest("input[action]")) {
      // submit ajax request to the specified action.
      var q = new XMLHttpRequest(),
        target = e.target.closest("input[action]"),
        action = target.getAttribute("action");
      q.open("get", action, true);
      q.send();

      // change from enable to disable and vise versa
      if (action.indexOf("enable") !== -1) {
        target.setAttribute("action", action.replace("enable", "disable"));
      } else {
        target.setAttribute("action", action.replace("disable", "enable"));
      }
    }
  });
})();
