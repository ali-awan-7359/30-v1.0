var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
// const bodyParser = require("body-parser");
var logger = require('morgan');
var app = express();

//aquiring data base
var mongoose = require("mongoose");

// Middleware to parse JSON bodies
// app.use(bodyParser.json())
app.use(express.json()); // For parsing application/json
app.use(express.urlencoded({ extended: true })); // For parsing application/x-www-form-urlencoded


// ROUTES
var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var patientSignUpRouter = require('./routes/patientSignUp');
var loginRouter = require('./routes/login');
var eyeTrackingRoute = require("./routes/eyeTracking");
var forgotPasswordRouter = require("./routes/forgotPassword");
var dashboardRouter = require("./routes/dashboard"); // Add this line



//connecting database
mongoose.connect("mongodb://0.0.0.0:27017/SDS")
  .then((db) => {
  console.log("Database connected!");
  console.log("http://localhost:9000");
}).catch((err) => {
  res.send(err);
})


// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
// Serve static files from the 'build' directory
app.use(express.static(path.join(__dirname, "frontend", "build")));
// //app.get("*", (req, res) => {
//   res.sendFile(path.join(__dirname, "frontend", "build", "index.html"));
// });

//CALLING ROUTES, MOUNT POINT
app.use('/', indexRouter);
app.use("/patientSignUp", patientSignUpRouter);
app.use("/login", loginRouter);
app.use('/users', usersRouter);
app.use("/eye-tracking", eyeTrackingRoute);
app.use("/forgot-password", forgotPasswordRouter);
app.use("/dashboard", dashboardRouter); // Add this line

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

app.get("/", (req, res) => {
  res.send("Hello World");
});



module.exports = app;
