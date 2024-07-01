// Call API and log data if response OK else log response
async function callApi() {
    try {
        const response = await fetch('/api');
        if (response.ok) {
            const data = await response.json();
            console.log(data);
        } else {
            throw new Error(`${response.status} (${response.statusText})`);
        }
    } catch (error) {
        console.error(error);
    }
}