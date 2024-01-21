// Function to add new data
function addData() {
    const rfid = $('#rfidInput').val();
    const plate = $('#plateInput').val();
    const bluetoothDevices = $('#bluetoothInput').val();

    // Validate input
    if (!rfid || !plate || !bluetoothDevices) {
        alert('RFID, Plate, and Bluetooth Device are required.');
        return;
    }

    $.ajax({
        type: 'POST',
        url: '/api/items',
        contentType: 'application/json',
        data: JSON.stringify({ rfid: rfid, plate: plate, bluetooth_devices: bluetoothDevices }),
        success: function (data) {
            // Resto del codice
        },
        error: function (error) {
            console.error(error);
            alert('Error adding data. Please try again.');
        }
    });

    fetchData();
}

// Function to fetch data from the server
function fetchData() {
    $.get('/api/items', function (data) {
        const dataList = $('#dataList');
        dataList.empty(); // Clear existing data

        // Reverse the order of items
        data.reverse();

        data.forEach(function (item) {

            const tableRow = $('<tr>');
            tableRow.append($('<td>').text(item.rfid));
            tableRow.append($('<td>').text(item.plate));
            tableRow.append($('<td>').text(item.bluetooth_devices));

            dataList.append(tableRow);
        });
    });
}

function fetchLastInserted() {
    $.get('/api/lastInserted', function (result) {
        const lastInsertedTable = $('<table>').addClass('lastInsertedTable');
        const tableBody = $('<tbody>');

        if (result.success) {
            // Se il successo è true, mostra i dati dell'ultimo inserimento
            const lastInserted = result.data;

            // Aggiungi una riga dell'intestazione
            const headerRow = $('<tr>');
            headerRow.append($('<th>').text('RFID'));
            headerRow.append($('<th>').text('Plate'));
            headerRow.append($('<th>').text('Bluetooth Devices'));
            tableBody.append(headerRow);

            // Aggiungi una riga di dati
            const dataRow = $('<tr>');
            dataRow.append($('<td>').text(lastInserted.rfid));
            dataRow.append($('<td>').text(lastInserted.plate));
            dataRow.append($('<td>').text(lastInserted.bluetooth_devices));
            tableBody.append(dataRow);
        } else {
            // Se il successo è false, mostra un messaggio di errore
            const errorRow = $('<tr>');
            errorRow.append($('<td>').attr('colspan', 3).text('Errore nel recupero dei dati'));
            tableBody.append(errorRow);
        }

        lastInsertedTable.append(tableBody);

        // Sostituisci il contenuto dell'elemento designato con la tabella
        $('#lastInsertedInfo').html(lastInsertedTable);

        // Supponendo che result.verification sia un booleano

        var verificationStateInfo = $('#VerificationStateInfo');
        var verificationResult = result.verification;

        if (verificationResult === true) {
            // Se il risultato della verifica è true, impostiamo il testo in verde e lo sfondo verde
            verificationStateInfo.text('TRUE').css({
                'color': 'white',
                'background-color': 'green',
                'padding': '5px', // opzionale, aggiunge spazio intorno al testo
                'border-radius': '5px' // opzionale, aggiunge bordi arrotondati
            });
        } else {
            // Se il risultato della verifica è false, impostiamo il testo in rosso e lo sfondo rosso
            verificationStateInfo.text('FALSE').css({
                'color': 'white',
                'background-color': 'red',
                'padding': '5px', // opzionale, aggiunge spazio intorno al testo
                'border-radius': '5px' // opzionale, aggiunge bordi arrotondati
            });
        }

    });
}



// Initial data fetch on document load
$(document).ready(function () {
    fetchData();
    // Set intervals to update every 2 seconds
    setInterval(fetchLastInserted, 2000);
});
