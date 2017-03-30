console.log(1);
tree_num = 0
var page = require('webpage').create();
page.viewportSize = { width: 800, height: 700 };
page.clipRect = { top: 0, left: 0, width: 800, height: 700 };

is_ready = false;
function createTreesImage(page, trees)
{ //#event-triggered programming...
  //create a table of all trees being printed
  //only when all trees being printed have called back will we close the program
  page.open('trees2.html', function ( ) {
    console.log(9);
    page.evaluate(function (t) {
      processTree(t);
      PrintTree(cxt,t);
    }, tree);
    page.render('tree_pic_' + (tree_num++) + '.png');
    page.close();
  });
}

console.log(20);
createTreeImage(page, {'text': 'PROJECT_{  S.sname  }', 'type': 'operator', 'children': [{'text': 'SELECT_{  S.rating = 5 }', 'type': 'operator', 'children': [{'text': 'CROSS', 'type': 'operator', 'children': [{'text': 'S', 'type': 'table', 'children': []}, {'text': 'R', 'type': 'table', 'children': []}]}]}]});
createTreeImage(page, {'text': 'PROJECT_{  S.sname2  }', 'type': 'operator', 'children': [{'text': 'SELECT_{  S.rating = 5 }', 'type': 'operator', 'children': [{'text': 'CROSS', 'type': 'operator', 'children': [{'text': 'S', 'type': 'table', 'children': []}, {'text': 'R', 'type': 'table', 'children': []}]}]}]});


phantom.exit();