var
  express = require('express'),
  fs = require('fs'),
  csv = require('fast-csv'),
  body_parser = require('body-parser');

// instantiate app
var app = express();

// static files middleware
app.use(express.static(__dirname + '/public'));
app.use('/jsPsych', express.static(__dirname + '/jsPsych'));

// body parsing middleware
app.use(body_parser.json());

// set template engine
app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html');


// setup views
app.set('views', __dirname + '/public/views');

// ICF route
app.get('/', function(request, response) {
    response.render('experiment.html', {
        js_filename: 'instructions',
        jspsych_plugins: ['instructions']
    });
});

var experiment_plugins = [
    'text',
    'instructions',
    'multi-stim-multi-response',
    'single-stim',
    'survey-multi-choice',
    'survey-text',
];

// practice route
app.get('/practice', function(request, response) {
    response.render('experiment.html', {
        js_filename: 'practice',
        jspsych_plugins: experiment_plugins
    });
});

// experiment route
app.get('/experiment', function(request, response) {
    response.render('experiment.html', {
        js_filename: 'experiment',
        jspsych_plugins: experiment_plugins
    });
});

// post-test questions route
app.get('/follow_up', function(request, response) {
    response.render('experiment.html', {
        js_filename: 'follow_up',
        jspsych_plugins: ['survey-multi-choice', 'text', 'survey-text']
    });
});

// experiment finished route
app.get('/finish', function(request, response) {
    response.render('finished.html');
});

// experiment data route
app.post('/experiment-data', function(request, response) {
  var
    headers = [
      "internal_chunk_id",
      "trial_index", "trial_index_global", "trial_type",
      "participant_id", "condition", "block_order",
      "block_stimuli", "block_type",
      "key_press", "responses", "rt", "time_elapsed",
      "correct", "response", "expected"
    ],
    file_path = ["data", request.body.pathname, request.body.filename + ".csv"].join('/');
  file_path = [
    __dirname,
    "data",
    request.body.pathname,
    request.body.filename + ".csv"
  ].join('/');

  // save data file
  csv
    .writeToPath(file_path, request.body.data, {headers: headers})
    .on("finish", function(){
      console.log("Finished writing to '" + file_path + "'");
    });

  response.end();
});


// start server
var server = app.listen(3000, function(){
    console.log("Listening on port %d", server.address().port);
});
