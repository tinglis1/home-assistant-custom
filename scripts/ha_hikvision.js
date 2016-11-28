#!/usr/bin/nodejs
var     ipcamera    = require('node-hikvision-api');
var     http        = require('http');

// Options:
var ha_Options = {
      host     : '192.168.0.100',
      port     : 8123,
      // username : 'user',
      password : 'password'
}

// options for hikvision camera
// required per camera
var optionsGate = {
    host    : '192.168.0.1',
    port    : '80',
    user    : 'username',
    pass    : 'password',
    log     : false,
};

var optionsFront = {
    host    : '192.168.0.2',
    port    : '80',
    user    : 'username',
    pass    : 'password',
    log     : false,
};

// one required per camera
var hikvisionGate   = new ipcamera.hikvision(optionsGate);
var hikvisionFront   = new ipcamera.hikvision(optionsFront);

console.log(getDateTime() + ' Started')

// Set initial state to no motion
setState('hikvision_event_gate_motion', 'off');
setState('hikvision_event_gate_line', 'off');


setState('hikvision_event_front_motion', 'off');
setState('hikvision_event_front_line', 'off');


// Monitor Camera Alarms
// requires one function per camera
hikvisionGate.on('alarm', function(code,action,index) {
    if (code === 'VideoMotion'   && action === 'Start')  {
        console.log(getDateTime() + ' Gate Channel ' + index + ': Video Motion Detected')
        setState('hikvision_event_gate_motion', 'on');
    }
    if (code === 'VideoMotion'   && action === 'Stop')   {
        console.log(getDateTime() + ' Gate Channel ' + index + ': Video Motion Ended')
        setState('hikvision_event_gate_motion', 'off');
    }
    if (code === 'LineDetection' && action === 'Start')  {
        console.log(getDateTime() + ' Gate Channel ' + index + ': Line Cross Detected')
        setState('hikvision_event_gate_line', 'on');
    }
    if (code === 'LineDetection' && action === 'Stop')   {
        console.log(getDateTime() + ' Gate Channel ' + index + ': Line Cross Ended')
        setState('hikvision_event_gate_line', 'off');
    }
});

// code = event reported by camera
// expected code values  AlarmLocal  VideoMotion  LineDetection  VideoLoss  VideoBlind
// action = Start or Stop
// index = camera index number in the camera device. almost always 1
hikvisionFront.on('alarm', function(code,action,index) {
    if (code === 'VideoMotion'   && action === 'Start')  {
        console.log(getDateTime() + ' Front Channel ' + index + ': Video Motion Detected')
        setState('hikvision_event_front_motion', 'on');
    }
    if (code === 'VideoMotion'   && action === 'Stop')   {
        console.log(getDateTime() + ' Front Channel ' + index + ': Video Motion Ended')
        setState('hikvision_event_front_motion', 'off');
    }
    if (code === 'LineDetection' && action === 'Start')  {
        console.log(getDateTime() + ' Front Channel ' + index + ': Line Cross Detected')
        setState('hikvision_event_front_line', 'on');
    }
    if (code === 'LineDetection' && action === 'Stop')   {
        console.log(getDateTime() + ' Front Channel ' + index + ': Line Cross Ended')
        setState('hikvision_event_front_line', 'off');
    }
});


function getDateTime() {
    var date = new Date();
    var hour = date.getHours();
    hour = (hour < 10 ? "0" : "") + hour;
    var min  = date.getMinutes();
    min = (min < 10 ? "0" : "") + min;
    var sec  = date.getSeconds();
    sec = (sec < 10 ? "0" : "") + sec;
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    month = (month < 10 ? "0" : "") + month;
    var day  = date.getDate();
    day = (day < 10 ? "0" : "") + day;
    return year + "-" + month + "-" + day + "T" + hour + ":" + min + ":" + sec;
}

function setState( item, newState ) {

    var headers = {
        'Content-Type': 'application/json',
        'x-ha-access': ha_Options['password']
    };

    var options = {
      host: ha_Options['host'],
      port: ha_Options['port'],
      path: '/api/states/binary_sensor.' + item,
      method: 'POST',
      headers: headers
    };

    var req = http.request(options, function(res) {
//    console.log('STATUS: ' + res.statusCode);
//    console.log('HEADERS: ' + JSON.stringify(res.headers));
      res.setEncoding('utf8');
      res.on('data', function (chunk) {
//      console.log('BODY: ' + chunk);
      });
    });

    req.on('error', function(e) {
//    console.log('problem with request: ' + e.message);
    });

    // write data to request body
    var data = {
        'state': newState,
        'attributes':
            {
              "sensor_class": "motion",
              "last_tripped_time": getDateTime()
            }
    };
    // console.log('DATA: ' + JSON.stringify(data));

    getDateTime()
    req.write(JSON.stringify(data));
    req.end();

}
