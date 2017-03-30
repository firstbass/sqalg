var page = require('webpage').create();
page.open('trees2.html', function() {
  page.evaluate(function ( ) {
    Tree = {'text': 'PROJECT_{  S.sname  }', 'type': 'operator', 'children': [{'text': 'SELECT_{  S.rating = 5 }', 'type': 'operator', 'children': [{'text': 'CROSS', 'type': 'operator', 'children': [{'text': 'S', 'type': 'table', 'children': []}, {'text': 'R', 'type': 'table', 'children': []}]}]}]};

    processTree(Tree);
    PrintTree(cxt,Tree);
  });
  page.render('github2.jpg');
  phantom.exit()
});