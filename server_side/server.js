const express = require('express');
const { MongoClient } = require('mongodb');
const app = express();
const port = 3000;


// Connection URI for MongoDB (replace with your actual connection string)
const uri = 'mongodb://192.168.137.1:27017/smartparking';
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
const url = 'https://192.168.137.37/receive-message';


app.use(express.static('public'));
app.use(express.json()); // Parse JSON requests
// Middleware per il parsing del corpo JSON

let pollingInterval;

let latestInsertedEntry = null;

async function fetchData() {
    try {

         // Get the current time in milliseconds
         var startTime = new Date().getTime();

        const database = client.db();
        const collection = database.collection('datadump');
        const items = await collection.find().toArray();

        if (items.length > 0) {
            // Log the latest entry
            latestInsertedEntry = items[items.length - 1];
            //console.log('Latest Inserted Entry:', latestInsertedEntry);
        } else {
            console.log('No entries in the collection.');
        }

         // Get the current time again
         var endTime = new Date().getTime();
         // Calculate the elapsed time in milliseconds
         var elapsedTime = endTime - startTime;
 
         // Convert milliseconds to seconds, minutes, or hours if needed
         var elapsedSeconds = elapsedTime / 1000;
         var elapsedMinutes = elapsedSeconds / 60;
         var elapsedHours = elapsedMinutes / 60;
 
        //console.log("[Fetch] Elapsed time in milliseconds: " + elapsedTime);
 
    } catch (error) {
        console.error('Polling error:', error);
    }
}

// Function to log collection names
async function logCollectionNames() {
    const database = client.db();
    const collections = await database.listCollections().toArray();
    const collectionNames = collections.map(collection => collection.name);
    //console.log('Collections in the database:', collectionNames);
}

// API endpoint to get all items
app.get('/api/items', async (req, res) => {
    try {
        await client.connect();
        console.log('Connected to MongoDB'); // Log statement indicating successful connection
        fetchData(); // Fetch data on initial request
        logCollectionNames(); // Log collection names on initial request
        // Start polling at a specified interval (e.g., every 2 seconds)
        pollingInterval = setInterval(fetchData, 2000);
        const database = client.db();
        const collection = database.collection('datadump');
        const items = await collection.find().toArray();

        //console.log(items);

        res.json(items);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// API endpoint to add new data
app.post('/api/items', async (req, res) => {
    try {

        console.log(req);

        const { rfid, plate, bluetooth_devices } = req.body;

        // Validation
        if (!rfid || !plate || !bluetooth_devices) {
            return res.status(400).json({ error: 'Invalid data format' });
        }

        await client.connect();
        const database = client.db();
        const collection = database.collection('datadump');

        // Insert the new data
        await collection.insertOne({ rfid, plate, bluetooth_devices });
        console.log("after insert one");

        // Log the inserted entry
        const insertedEntry = { rfid, plate, bluetooth_devices };
        console.log('Inserted Entry:', insertedEntry);

        res.json({ success: true, message: 'Data added successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// API endpoint to get the last inserted entry
// ... (altre importazioni e configurazioni)

// API endpoint per ottenere l'ultimo elemento inserito con un valore booleano
app.get('/api/lastInserted', async (req, res) => {
    try {
        // Get the current time in milliseconds
        var startTime = new Date().getTime();

        // Perform some operations or wait for a certain event

        

        if (latestInsertedEntry) {
            const database = client.db(); // Assicurati di avere il riferimento al database
            const testCollection = database.collection('employees');
            const suspendedCollection = database.collection('suspended');

            const items = await testCollection.find().toArray();  
            
            console.log(items);
            

            // Trova un elemento nella collezione 'test' che corrisponda ai dati dell'ultimo inserimento
            const plateRFID = await testCollection.find({
                $and: [
                    { rfid: latestInsertedEntry.rfid },
                    { plate: latestInsertedEntry.plate }
                ]
            }).toArray();

            const plateBt = await testCollection.find({
                $and: [
                    { plate: latestInsertedEntry.plate },
                    { bluetooth_devices: latestInsertedEntry.bluetooth_devices},
                ]
            }).toArray();



            const RFIDbt = await testCollection.find({
                $and: [
                    { rfid: latestInsertedEntry.rfid },
                    { bluetooth_devices: latestInsertedEntry.bluetooth_devices},
                ]
            }).toArray();

        

            /*
            const all = await testCollection.find({
                $or: [
                    { _id: latestInsertedEntry._id },
                    { plate: latestInsertedEntry.plate },
                    { bluetooth_devices: latestInsertedEntry.bluetooth_devices },
                ]
            }).toArray();*/

            console.log(RFIDbt);
            console.log(plateRFID);
            console.log(plateBt);

            // Check if the IDs are not in the suspendedCollection
            const isRFIDbtSuspended = await suspendedCollection.find({ id: RFIDbt[0].id });
            const isPlateBtSuspended = await suspendedCollection.find({ id: plateBt[0].id });
            const isPlateRFIDSuspended = await suspendedCollection.find({ id: plateRFID[0].id });

            

            console.log("susp: "+isPlateBtSuspended.data);
            console.log("susp: "+isRFIDbtSuspended.data);
            console.log("susp: "+isPlateRFIDSuspended.data);
         

            if ((RFIDbt.length == 1 && !isRFIDbtSuspended) || (plateBt.length == 1 && !isPlateBtSuspended) || (plateRFID.length == 1 && !isPlateRFIDSuspended)) {
                // Se esiste un elemento corrispondente e non è sospeso, imposta verification a true
                
                console.log(RFIDbt);
                console.log(plateRFID);
                console.log(plateBt);
                


                const idToSuspend = RFIDbt.length === 1 ? RFIDbt[0].id :
                                    plateBt.length === 1 ? plateBt[0].id :
                                    plateRFID.length === 1 ? plateRFID[0].id : null;
                if (idToSuspend) {
                    // Assuming 'suspendedCollection' is your MongoDB collection

                    // Create a TTL index on the 'createdAt' field with an expiration time of 22 hours (79200 seconds)
                    await suspendedCollection.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 79200 });

                    // Now, when you insert a document with a 'createdAt' field, MongoDB will automatically remove it after 22 hours
                    await suspendedCollection.insertOne({ id: idToSuspend, createdAt: new Date() });

                    console.log("Inserted in suspended");
                }

                

                    
                verification = true;
            } else {
                // Se non esiste un elemento corrispondente o è sospeso, imposta verification a false
                verification = false;
                
             
            }

            // Invia un oggetto JSON che include i dati dell'ultimo inserimento e il valore booleano di verification
            res.json({ data: latestInsertedEntry, success: true, verification: verification });
            const https = require('https');
            
           const data = verification ? "data=open" : "data=close";


            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': Buffer.byteLength(data),
                },
                rejectUnauthorized: false, // Ignore SSL certificate verification (use with caution)
            };

            const req = https.request(url, options, (res) => {
                let responseData = '';

                res.on('data', (chunk) => {
                    responseData += chunk;
                });

                res.on('end', () => {
                    console.log('Response:', responseData);
                });
            });

            req.on('error', (error) => {
                console.error('Error:', error.message);
            });

            // Send the POST data
            req.write(data);
            req.end();

        } else {
            res.json({ message: 'Nessun elemento è stato inserito ancora.', success: false });
        }

        // Get the current time again
        var endTime = new Date().getTime();
        // Calculate the elapsed time in milliseconds
        var elapsedTime = endTime - startTime;

        // Convert milliseconds to seconds, minutes, or hours if needed
        var elapsedSeconds = elapsedTime / 1000;
        var elapsedMinutes = elapsedSeconds / 60;
        var elapsedHours = elapsedMinutes / 60;

        //console.log("[LastEntry] Elapsed time in milliseconds: " + elapsedTime);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Errore interno del server', success: false });
    }
});





app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});

// Close the polling interval when the server is shutting down
process.on('SIGINT', () => {
    clearInterval(pollingInterval);
    console.log('Server shutting down...');
    process.exit();
});
    