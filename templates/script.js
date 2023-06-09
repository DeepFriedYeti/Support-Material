function addPage() {
    var numPages = parseInt(document.getElementById('numPages').value);
    var container = document.getElementById('pagesContainer');

    for (var i = 0; i < numPages; i++) {
        var pageDiv = document.createElement('div');
        pageDiv.classList.add('page');

        var pageLabel = document.createElement('label');
        pageLabel.innerHTML = 'Page ' + (i + 1);

        var drawingInput = document.createElement('input');
        drawingInput.type = 'file';
        drawingInput.name = 'drawing' + i;
        drawingInput.accept = 'image/png, image/jpeg';

        var mainInput = document.createElement('input');
        mainInput.type = 'file';
        mainInput.name = 'main' + i;
        mainInput.accept = 'image/png, image/jpeg';

        pageDiv.appendChild(pageLabel);
        pageDiv.appendChild(document.createElement('br'));
        pageDiv.appendChild(document.createTextNode('Drawing: '));
        pageDiv.appendChild(drawingInput);
        pageDiv.appendChild(document.createElement('br'));
        pageDiv.appendChild(document.createTextNode('Main: '));
        pageDiv.appendChild(mainInput);

        container.appendChild(pageDiv);
    }
}

document.getElementById('pageForm').addEventListener('submit', function (event) {
    var numPages = parseInt(document.getElementById('numPages').value);
    var pageDivs = document.getElementsByClassName('page');

    // Check if all pages are filled
    if (numPages !== pageDivs.length) {
        alert('Please fill all the pages.');
        event.preventDefault(); // Prevent form submission
    }
});