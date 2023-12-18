const svg = document.getElementsByTagName('svg').item(0)

const engine = new liquidjs.Liquid()
var data = {}

const elements = Array.prototype.slice.call(document.getElementsByTagName('liquid')).forEach(element => {
  data[element.getAttribute("name")] = element.getAttribute("value")
})

engine
	.parseAndRender(svg.outerHTML, {"data": data})
	.then(html => svg.outerHTML = html)