const $body = $("body");

const RATINGS = {
    "0": "regular_0.png",
    "1": "regular_1.png",
    "1.5": "regular_1_half.png",
    "2": "regular_2.png",
    "2.5": "regular_2_half.png",
    "3": "regular_3.png",
    "3.5": "regular_3_half.png",
    "4": "regular_4.png",
    "4.5": "regular_4_half.png",
    "5": "regular_5.png"
}


// /**
//  * Retrieve form data and turn it into an object
//  * POST the object to the get-lucky-num route
//  * Take the JSON response and pass to the handleResponse function
//  * 
//  * Note: Axios will automatically serialize the dictionary into JSON, and create header content-type of "application/json"
//  * JSON.stringify can be used to provide JSON, but the content-type must be specified
//  * source: https://masteringjs.io/tutorials/axios/post-json
//  * 
//  *//

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

    handleResponse(res.data.businesses)
}


function handleResponse(businesses) {

    $('#results-header').html("Here's what's nearby:")

    for (const business of businesses) {

        const rating = business.rating;

        const image_path = `static/images/stars/${RATINGS[rating]}`;

        let priceDisplay = "";
        let phoneDisplay = "";

        if (business.price == undefined) {
            priceDisplay = "display: none;"
        }

        if (!business.phone) {
            phoneDisplay = "display: none;"
        }

        $('#search-results').append(`
        <div class="container mb-2 p-1 rounded" style="background-color: #EDF5E1;">
        <div class="row justify-content-center">
        <div class="d-none d-md-inline col-md-2 text-center my-auto">
        <img src=${business.image_url} class="rounded contain">
        </div>
        <div class="col-6 col-md-5 text-center">
        <p class="fw-bold" style="font-size: 1.2rem; color: #05386B;">${business.name}</p>
        <p class="info"><img class="mb-2" src="${image_path}"></p>
        <p class="info d-none d-md-inline m-2 fw-bold">Category: <span
                class="fw-normal">${business.categories[0]["title"]}</span></p>
        <p class="info fw-bold" style="${priceDisplay}">Price: <span class="fw-normal">${business.price}</span></p>
        </div>

        <div class="col-6 col-md-3 text-center">
        <p class=" mt-3 address">${business.location.display_address[0]}</p>
        <p class="address">${business.location.display_address[1]}</p>
        <p class="info mt-2 fw-bold" style="${phoneDisplay}">Phone: <span class="fw-normal">${business.phone}</span>
        </p>
        <a href=${business.url} class="d-none d-md-inline url"><img class="m-3" src="static/images/yelp_logo.png"
                    style="width: 75px;"></a>
        </div>
        <div class="col-12 col-md-2 align-self-center text-center">
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
        <input type="hidden" id="rating" name="rating" value="${image_path}">
        <input type="hidden" id="phone" name="phone" value="${business.phone}">
        <button type="submit" class="save-button btn-warning btn-lg">Save!</button>
        </form>
        <a href=${business.url} class="d-md-none url"><img class="m-3" src="static/images/yelp_logo.png"
                    style="width: 75px;"></a>
        </div>
        </div>
        </div>
        `)
    }

    // <input type="hidden" id="category" name="category" value="${business.categories[0]["title"]}">
    // <input type="hidden" id="name" name="name" value="${business.name}">
    // <input type="hidden" id="url" name="url" value="${business.url}">
    // <input type="hidden" id="image_url" name="image_url" value="${business.image_url}">
    // <input type="hidden" id="address_0" name="address_0" value="${business.location.display_address[0]}">
    // <input type="hidden" id="address_1" name="address_1" value="${business.location.display_address[1]}">
    // <input type="hidden" id="price" name="price" value="${business.price}">
    // <input type="hidden" id="rating" name="rating" value="${image_path}">
    // <input type="hidden" id="phone" name="phone" value="${business.phone}">


    // clear inputs if successful
    $('#category').val('');
    $('#city').val('');
}

/**
 * 
 * Save a place from the search results
 */
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

    // submit place Id to server to be stored in db
    const placeIdObj = {
        placeId
    }

    const res = await axios.post(`places/save`, placeIdObj);

    if (res.data.message == "added") {
        $button.text('Saved!');
        $button.removeClass('btn-warning');
        $button.addClass('btn-success');

    } else if (res.data.message == "not added") {
        alert("Log in to start saving places!");
    }
}


/**
 * Remove a saved place
 */
async function removePlace(evt) {

    evt.preventDefault();

    const $button = $(evt.target);

    const placeId = $button.data("id");

    await axios.post(`/places/${placeId}/delete`);

    $button.closest("div.accordion-item").remove();
}





/**
 * Event handlers for submitting search form,
 * Saving a place,
 * and removing a saved place
 */
$("#search-form").on("submit", processForm);

$body.on("click", ".save-button", savePlace);

$(".remove-button").on("click", removePlace);





