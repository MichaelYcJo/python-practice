import axios from "axios";

const callApi = async (method, path, data, params = {}) => {

    const baseUrl = `http://127.0.0.1:8000/api/v1`;
    const fullUrl = `${baseUrl}${path}`;
    if (method === "get" || method === "delete") {
        return axios[method](fullUrl, { params });
    } else {
        return axios[method](fullUrl, data);
    }
};

const apiList = {
    createAccount: form => callApi("post", "/accounts/register/", form)

};

export default apiList;
