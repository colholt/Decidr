'use strict';

/**
 * @ngdoc function
 * @name decidrApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the decidrApp
 */
angular.module('decidrApp')
  .controller('MainCtrl', function ($scope, $http) {
    $scope.roomID;
    $scope.userID;
    $scope.idError = false;
    $scope.createdRoom = false;

    $scope.createRoom = function () {
      var data = { "name": $scope.name, "roomName": $scope.roomName };
      $http.post('http://68.183.140.180:5000/createRoom', data).then(function (res) {
        $scope.roomID = res.data.roomID;
        $scope.userID = res.data.userID;
        console.log("room id:", res.data.roomID);
        var url = "http://68.183.140.180:5000/subscribe?roomid=";
        url += $scope.roomID;
        $scope.choices = [];
        var source = new EventSource(url); //setup event source for SSE
        $scope.createdRoom = true;
        // process event from server
        source.onmessage = function (event) {
          var data = event.data.split('\n');
          console.log(data);
          var fixed_data = JSON.parse(data[0].split("'data': ")[1].split("'}")[0].slice(1));
          if (fixed_data.type === "choice") {
            $scope.$apply(function () {
              $scope.choices.push([fixed_data.choiceID, fixed_data.choice]);
            });
            console.log($scope.choices);
          }
        };

        $scope.changeView("view");
      }, function (res) {
        console.log("failure", res);
      });
    };

    $scope.joinRoom = function () {
      var data = { "name": $scope.name, "roomID": $scope.rid };
      $http.post('http://68.183.140.180:5000/joinRoom', data).then(function (res) {
        // handle successful room join
        $scope.roomID = res.data.roomID;
        $scope.userID = res.data.userID;
        $scope.idError = false;
        var url = "http://68.183.140.180:5000/subscribe?roomid=";
        url += $scope.roomID;
        $scope.roomName = res.data.roomName;
        $scope.choices = res.data.choices;
        $scope.createdRoom = false;
        $scope.changeView("view");
        var source = new EventSource(url); //setup event source for SSE

        source.onmessage = function (event) {
          // process event from server
          var data = event.data.split('\n');
          console.log(data);
          try {
            var fixed_data = JSON.parse(data[0].split("'data': ")[1].split("'}")[0].slice(1));
            if (fixed_data.type === "choice") {
              $scope.$apply(function () {
                $scope.choices.push([fixed_data.choiceID, fixed_data.choice]);
              });
              console.log($scope.choices);
            }
          } catch (err) {
            //no
          }
        };
      }, function (res) {
        // handle room not joined
        if (res.data === "RoomID not valid") {
          $scope.idError = true;
        }

        console.log("err:", res);
      });
    };


    $scope.addChoice = function () {
      var data = {"roomID": $scope.roomID, "choice": $scope.choice};
      $http.post('http://68.183.140.180:5000/addChoice', data).then(function (res) {
        console.log(res);
        $scope.choice = "";
      }, function (res) {
        console.log('err',res);
      });
    };

    $scope.makeDecision = function () {
      
    };


    // Function to change view
    $scope.changeView = function (name) {
      if (name === "join") {
        $scope.joining = true;
        $scope.creating = false;
      }
      if (name === "create") {
        $scope.joining = false;
        $scope.creating = true;
      }
      if (name === "view") {
        $scope.joining = false;
        $scope.creating = false;
        $scope.view = true;
      }
      if (name === "home") {
        $scope.joining = false;
        $scope.creating = false;
        $scope.view = false;
      }
    };
  });
