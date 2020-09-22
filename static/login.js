
window._public_key = "00A6802E721FE2F171BF372CADDC8BEAD7F9C310CFB42DD981061935CC0768152581E54C03CD3F4983782CF7B75607007BA3BBCB5976D28DFA5D9B49BC5BA010D3";

async function handleLoginFormSubmit (e) {
    e.preventDefault()
    e.stopPropagation();

    const formData = $(this)
        .serializeArray()
        .reduce((acc, val) => ({
            ...acc,
            [val.name]: val.value
        }), {})

    const responseData = await Cralwer.checkAuth(fnRSAEnc(formData.id), fnRSAEnc(formData.password))

    switch (responseData.code) {
        case "504":
        case "200":
            localStorage.setItem('_decodeUserId', formData.id)
            localStorage.setItem('_userId', btoa(fnRSAEnc(formData.id), "HaNyAnGbLaCkBoArD"));
            localStorage.setItem('_userPassword', btoa(fnRSAEnc(formData.password), "HaNyAnGbLaCkBoArD"));

            alert("로그인 성공!!");
            location.href = '/';
            break;
        default:
            alert("올바르지 않은 아이디 또는 비밀번호 입니다.");

    }

    console.log(responseData);
    return false;
}


$("#login-form").on('submit', handleLoginFormSubmit)