


const $body = $("body");


// /**
//  * Retrieve form data and turn it into an object
//  * POST the object to the get-lucky-num route
//  * Take the JSON response and pass to the handleResponse function
//  * 
//  * Note: Axios will automatically serialize the dictionary into JSON, and create header content-type of "application/json"
//  * JSON.stringify can be used to provide JSON, but the content-type must be specified
//  * source: https://masteringjs.io/tutorials/axios/post-json
//  * 
//  */

async function processForm(evt) {

    evt.preventDefault()

    // clear previous search results
    $('#search-results').html('')

    const category = $('#category').val();
    const city = $('#city').val();

    const inputObj = {
        category,
        city
    }

    const res = await axios.post("/search", inputObj)

    // console.log(res.data.businesses)

    handleResponse(res.data.businesses)
}


function handleResponse(businesses) {

    $('#results-col').prepend(`
    <h2>Here's what's nearby:</h2>
    `)

    for (const business of businesses) {
        $('#search-results').append(`
        <div class="container mb-2 p-3 border border-dark bg-secondary rounded result">
        <div class="row">
            <div class="col-2">
                <img src=${business.image_url} class="rounded" style="width:125px; height:125px;">
            </div>
            <div class="col-4">
            <p class="text-white" style="font-size: 2rem;">${business.name}</p>
            <p class="info text-white">Category: ${business.categories[0]["title"]}</p>
            <p class="info text-white">Rating: ${business.rating}/5</p>
            <p class="info text-white">Price: ${business.price}</p>
            </div>

            <div class="col-4">
            <p class="info text-white">Phone: ${business.phone}/5</p>
            <p class="address text-white">${business.location.display_address[0]}</p>
            <p class="address text-white">${business.location.display_address[1]}</p>
            <a href=${business.url} class="url">More Info</a>
            </div>

            <div class="col-2 align-self-center">

            <form class="save-form">

            <input type="hidden" id="place-id" name="placeId" value="${business.id}">
            <input type="hidden" id="category" name="category" value="${business.categories[0]["title"]}">
            <input type="hidden" id="name" name="name" value="${business.name}">
            <input type="hidden" id="url" name="url" value="${business.url}">
            <input type="hidden" id="image_url" name="image_url" value="${business.image_url}">
            <input type="hidden" id="address_0" name="address_0" value="${business.location.display_address[0]}">
            <input type="hidden" id="address_1" name="address_1" value="${business.location.display_address[1]}">
            <input type="hidden" id="address_0" name="address_0" value="${business.location.display_address[0]}">
            <input type="hidden" id="address_1" name="address_0" value="${business.location.display_address[1]}">
            <input type="hidden" id="price" name="price" value="${business.price}">
            <input type="hidden" id="rating" name="rating" value="${business.rating}">
            <input type="hidden" id="phone" name="phone" value="${business.phone}">
            <button type="submit" class="save-button btn-warning btn-lg">Save!</button>
            </form>  
            </div>
        </div>
        </div>
        `)
    }


    // clear inputs if successful
    $('#category').val('');
    $('#city').val('');
}





async function removePlace(evt) {

    evt.preventDefault();

    const $button = $(evt.target);

    const placeId = $button.data("id");

    await axios.post(`/places/${placeId}/delete`);

    $button.closest("div.container").remove();
}



async function savePlace(evt) {

    evt.preventDefault();

    const $button = $(evt.target);

    // must specify "this" to get correct form data
    const name = $('input[name=name]', this.form).val();
    const url = $('input[name=url]', this.form).val();
    const image_url = $('input[name=image_url]', this.form).val();
    const placeId = $('input[name=placeId]', this.form).val();
    const category = $('input[name=category]', this.form).val();
    const address_0 = $('input[name=address_0]', this.form).val();
    const address_1 = $('input[name=address_1]', this.form).val();
    const price = $('input[name=price]', this.form).val();
    const rating = $('input[name=rating]', this.form).val();
    const phone = $('input[name=phone]', this.form).val();

    const inputObj = {
        name,
        url,
        image_url,
        placeId,
        category,
        address_0,
        address_1,
        price,
        rating,
        phone
    }

    $button.text('Saved!');
    $button.removeClass('btn-warning');
    $button.addClass('btn-success');

    // console.log(inputObj);

    const res = await axios.post(`places/save`, inputObj);
    // console.log(res);
}

// form submit event handler
$("#search-form").on("submit", processForm);

// $(".save-button").on("click", savePlace);

$(".remove-button").on("click", removePlace);

// favorite toggle click event handler
$body.on("click", ".save-button", savePlace);





