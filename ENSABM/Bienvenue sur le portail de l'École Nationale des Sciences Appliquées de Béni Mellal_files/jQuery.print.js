/* @license 
 * jQuery.print, version 1.6.2
 * Licence: CC-By (http://creativecommons.org/licenses/by/3.0/)
 *--------------------------------------------------------------------------*/
(function($){'use strict';function jQueryCloneWithSelectAndTextAreaValues(elmToClone,withDataAndEvents,deepWithDataAndEvents){var $elmToClone=$(elmToClone),$result=$elmToClone.clone(withDataAndEvents,deepWithDataAndEvents),$myTextareas=$elmToClone.find('textarea').add($elmToClone.filter('textarea')),$resultTextareas=$result.find('textarea').add($result.filter('textarea')),$mySelects=$elmToClone.find('select').add($elmToClone.filter('select')),$resultSelects=$result.find('select').add($result.filter('select')),$myCanvas=$elmToClone.find('canvas').add($elmToClone.filter('canvas')),$resultCanvas=$result.find('canvas').add($result.filter('canvas')),i,l,j,m,myCanvasContext;for(i=0,l=$myTextareas.length;i<l;++i){$($resultTextareas[i]).val($($myTextareas[i]).val())}
for(i=0,l=$mySelects.length;i<l;++i){for(j=0,m=$mySelects[i].options.length;j<m;++j){if($mySelects[i].options[j].selected===!0){$resultSelects[i].options[j].selected=!0}}}
for(i=0,l=$myCanvas.length;i<l;++i){myCanvasContext=$myCanvas[i].getContext('2d');if(myCanvasContext){$resultCanvas[i].getContext('2d').drawImage($myCanvas[i],0,0);$($resultCanvas[i]).attr('data-jquery-print',myCanvasContext.canvas.toDataURL())}}
return $result}
function getjQueryObject(string){var jqObj=$('');try{jqObj=jQueryCloneWithSelectAndTextAreaValues(string)}catch(e){jqObj=$('<span />').html(string)}
return jqObj}
function printFrame(frameWindow,content,options){var def=$.Deferred();try{frameWindow=frameWindow.contentWindow||frameWindow.contentDocument||frameWindow;try{frameWindow.resizeTo(window.innerWidth,window.innerHeight)}catch(err){console.warn(err)}
var wdoc=frameWindow.document||frameWindow.contentDocument||frameWindow;if(options.doctype){wdoc.write(options.doctype)}
wdoc.write(content);try{var canvas=wdoc.querySelectorAll('canvas');for(var i=0;i<canvas.length;i++){var ctx=canvas[i].getContext('2d');var image=new Image();image.onload=function(){ctx.drawImage(image,0,0)};image.src=canvas[i].getAttribute('data-jquery-print')}}catch(err){console.warn(err)}
wdoc.close();var printed=!1,callPrint=function(){if(printed){return}
frameWindow.focus();try{if(!frameWindow.document.execCommand('print',!1,null)){frameWindow.print()}
$('body').focus()}catch(e){frameWindow.print()}
frameWindow.close();printed=!0;def.resolve()};$(frameWindow).on('load',callPrint);setTimeout(callPrint,options.timeout)}catch(err){def.reject(err)}
return def}
function printContentInIFrame(content,options){var $iframe=$(options.iframe+'');var iframeCount=$iframe.length;if(iframeCount===0){$iframe=$('<iframe height="0" width="0" border="0" wmode="Opaque"/>').prependTo('body').css({'position':'absolute','top':-999,'left':-999,})}
var frameWindow=$iframe.get(0);return printFrame(frameWindow,content,options).done(function(){setTimeout(function(){if(iframeCount===0){$iframe.remove()}},1000)}).fail(function(err){console.error('Failed to print from iframe',err);printContentInNewWindow(content,options)}).always(function(){try{options.deferred.resolve()}catch(err){console.warn('Error notifying deferred',err)}})}
function printContentInNewWindow(content,options){var frameWindow=window.open();return printFrame(frameWindow,content,options).always(function(){try{options.deferred.resolve()}catch(err){console.warn('Error notifying deferred',err)}})}
function isNode(o){return!!(typeof Node==='object'?o instanceof Node:o&&typeof o==='object'&&typeof o.nodeType==='number'&&typeof o.nodeName==='string')}
$.print=$.fn.print=function(){var options,$this,self=this;if(self instanceof $){self=self.get(0)}
if(isNode(self)){$this=$(self);if(arguments.length>0){options=arguments[0]}}else{if(arguments.length>0){$this=$(arguments[0]);if(isNode($this[0])){if(arguments.length>1){options=arguments[1]}}else{options=arguments[0];$this=$('html')}}else{$this=$('html')}}
var defaults={globalStyles:!0,mediaPrint:!1,stylesheet:null,noPrintSelector:'.no-print',iframe:!0,append:null,prepend:null,manuallyCopyFormValues:!0,deferred:$.Deferred(),timeout:750,title:null,doctype:'<!doctype html>',};options=$.extend({},defaults,(options||{}));var $styles=$('');if(options.globalStyles){$styles=$('style, link, meta, base, title')}else if(options.mediaPrint){$styles=$('link[media=print]')}
if(options.stylesheet){if(!(($.isArray?$.isArray:Array.isArray)(options.stylesheet))){options.stylesheet=[options.stylesheet]}
for(var i=0;i<options.stylesheet.length;i++){$styles=$.merge($styles,$('<link rel="stylesheet" href="'+options.stylesheet[i]+'">'))}}
var copy=jQueryCloneWithSelectAndTextAreaValues($this,!0,!0);copy=$('<span/>').append(copy);copy.find(options.noPrintSelector).remove();copy.append(jQueryCloneWithSelectAndTextAreaValues($styles));if(options.title){var title=$('title',copy);if(title.length===0){title=$('<title />');copy.append(title)}
title.text(options.title)}
copy.append(getjQueryObject(options.append));copy.prepend(getjQueryObject(options.prepend));if(options.manuallyCopyFormValues){copy.find('input').each(function(){var $field=$(this);if($field.is('[type=\'radio\']')||$field.is('[type=\'checkbox\']')){if($field.prop('checked')){$field.attr('checked','checked')}}else{$field.attr('value',$field.val())}});copy.find('select').each(function(){var $field=$(this);$field.find(':selected').attr('selected','selected')});copy.find('textarea').each(function(){var $field=$(this);$field.text($field.val())})}
var content=copy.html();try{options.deferred.notify('generated_markup',content,copy)}catch(err){console.warn('Error notifying deferred',err)}
copy.remove();if(options.iframe){try{printContentInIFrame(content,options)}catch(e){console.error('Failed to print from iframe',e.stack,e.message);printContentInNewWindow(content,options)}}else{printContentInNewWindow(content,options)}
return this}})(jQuery)