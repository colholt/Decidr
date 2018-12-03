'use strict';

/**
 * @ngdoc function
 * @name decidrApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the decidrApp
 */
angular.module('decidrApp')
  .controller('MainCtrl', function ($scope) {
    $scope.changeView = function(name) {
      if (name === "join") {
        $scope.joining = true;
        $scope.creating = false;
      }
      if (name === "create") {
        $scope.joining = false;
        $scope.creating = true;
      }
      if (name === "home") {
        $scope.joining = false;
        $scope.creating = false;
      }
    };
  });
