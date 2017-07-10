/*
 * File Name : date.js
 *
 * Copyright (C) 2017 Gaston TJEBBES g.t@majerti.fr
 * Company : Majerti ( http://www.majerti.fr )
 *
 * This software is distributed under GPLV3
 * License: http://www.gnu.org/licenses/gpl-3.0.txt
 *
 */
var dateutils = {
    parseDate: function(isoDate){
    /*
     * Returns a js Date object from an iso formatted string
     */
        var splitted = isoDate.split('-');
        var year = parseInt(splitted[0], 10);
        var month = parseInt(splitted[1], 10) - 1;
        var day = parseInt(splitted[2], 10);
        return new Date(year, month, day);
    },
	getDateFromIso: function(isoDateStr, dateFormat){
	 var strdate = "";
	 if (isoDateStr !== ''){
	  var date = dateutils.parseDate(isoDateStr);
	  strdate = $.datepicker.formatDate(dateFormat, date);
	 }
	 return strdate;
	},
	getTimeFromIso: function(isoTimeStr, timeFormat){
	  var splitted = isoTimeStr.split(':');
	  var hour = parseInt(splitted[0], 10);
	  var min = parseInt(splitted[1], 10);
	  return $.datepicker.formatTime(timeFormat, {hour: hour, minute: min});
	},
	getDateTimeFromIso: function(isoStr, dateFormat, timeFormat){
	  var strdatetime = "";
	  if (isoStr !== ''){
		var isoDateStr = isoStr.split(' ')[0];
		var isoTimeStr = isoStr.split(' ')[1];
		var strdate = dateutils.getDateFromIso(isoDateStr, dateFormat);
		var strTime = dateutils.getTimeFromIso(isoTimeStr, timeFormat);
		strdatetime = strdate + " " + strTime;
	  }
	  return strdatetime;
	}
}
