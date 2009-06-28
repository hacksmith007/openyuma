<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
  <head>
    <meta content="text/html; charset=utf-8"
	  http-equiv="Content-Type" py:replace="''"/>
    <link media="screen" href="/tg_widgets/turbogears.widgets/tabber/tabber.css"
	  type="text/css" rel="stylesheet"/>
    <title>Netconf Central Grouping Usage Search Results</title>
  </head>
  <body>
    <h1>Grouping Usage Search Results</h1>
    <div class="ncmain">
      <?python row = "0" ?>
      <table id="tablist" border="1">
	<tr id="tabheader">
	  <td>Object</td>
	  <td>Type Name</td>
	  <td>Module</td>
	  <td>Version</td>
	</tr>
	<tr py:for="ncobject in ncobjects" id="tablist">
	  <?python
	     if row =="0":
                 row = "1"
                 idfill = "tablist_odd"
	     else:
                 row = "0"
                 idfill = "tablist_even"
	     ?>
	  <td id="${idfill}">
	    <a href="${tg.url(ncobject.docurl)}"
	       py:content="ncobject.name"/>
	  </td>
	  <td id="${idfill}" py:content="ncobject.typename"/>
	  <td id="${idfill}" py:content="ncobject.modname"/>
	  <td id="${idfill}" py:content="ncobject.version"/>
        </tr>
      </table>
    </div>
  </body>
</html>
