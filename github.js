var tree_num = 0
var page = require('webpage').create(),
    system = require('system'),
    tree_string, name;

if (system.args.length < 0 || system.args.length > 1)
  phantom.exit(1);

if (system.args.length == 1)
  name = system.args[0];

// page information
page.viewportSize = { width: 800, height: 700 };
page.clipRect = { top: 0, left: 0, width: 800, height: 700 };

//function createTreeImage(page, trees)
//{ //#event-triggered programming...
  //create a table of all trees being printed
  //only when all trees being printed have called back will we close the program

function loadJSON(callback) {
  var xobj = new XMLHttpRequest();
  xobj.overrideMimeType("application/json");
  xobj.open('GET', 'json_data.json', true);
  // Replace 'my_data' with the path to your file
  xobj.onreadystatechange = function() {
    if (xobj.readyState == 4 && xobj.status == "200") {
      // Required use of an anonymous callback 
      // as .open() will NOT return a value but simply returns undefined in asynchronous mode
      callback(xobj.responseText);
    }
  };
  xobj.send(null);
}

loadJSON(function(response) {
  // Parse JSON string into object
  try {
    var tree = JSON.parse(response);
  }
  catch (e) {
    console.log(e);
    phantom.exit(1);
  }
  page.open('trees2.html', function ( ) {
    page.evaluate(function (t) {
      processTree(t);
      PrintTree(cxt,t);
    }, tree);
    if (!name)
      page.render('tree_pic_' + Math.random() + '.png');
    else
      page.render(name);
    page.close();
    phantom.exit(0);
  });
});

//createTreeImage(page, {'text': 'PROJECT_{  S.sname  }', 'type': 'operator', 'children': [{'text': 'SELECT_{  S.rating = 5 }', 'type': 'operator', 'children': [{'text': 'CROSS', 'type': 'operator', 'children': [{'text': 'S', 'type': 'table', 'children': []}, {'text': 'R', 'type': 'table', 'children': []}]}]}]});
//createTreeImage(page, {'text': 'PROJECT_{  S.sname2  }', 'type': 'operator', 'children': [{'text': 'SELECT_{  S.rating = 5 }', 'type': 'operator', 'children': [{'text': 'CROSS', 'type': 'operator', 'children': [{'text': 'S', 'type': 'table', 'children': []}, {'text': 'R', 'type': 'table', 'children': []}]}]}]});


//phantom.exit();