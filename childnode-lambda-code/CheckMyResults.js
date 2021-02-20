const AWS = require("aws-sdk");
var fs = require('fs');
var path = require('path');
const s3 = new AWS.S3();
var params;
exports.handler = async function (event, context) {
  let folder = event.key.split('/')[0];
  params = {
    Bucket: event.buket_out,
    Delimiter: '/',
    Prefix: folder + '/'
  };

  try {
    let data = await s3.listObjects(params).promise();
    let namehtml = event.newFileName || 'ListOfResult.html';
    let html = create_resume_page(data, namehtml, event);
    let download_path = `/tmp/${namehtml}`;
    create_file(download_path, html)
    let result = await upload_to_s3(params.Bucket, params.Prefix, download_path)
    let succes = await putObject_to_s3(params.Bucket, result.key, download_path)
    result.message = "Check and Summary HTML Created"
    context.succeed(result);
  } catch (e) {
    console.log({ e })
    context.succeed("error on code");
  }
};

function upload_to_s3(bucketName, keyPrefix, filePath) {
  var fileName = path.basename(filePath);
  var fileStream = fs.createReadStream(filePath);
  // Save to "alucloud-lambda-out/{prefix}/{filename}"
  //     ex: "alucloud-lambda-out/32/example.html"
  var keyName = path.join(keyPrefix, fileName);
  // Wrap this in a promise so that it's possible handle a fileStream error
  // since it can happen *before* s3 actually reads the first 'data' event
  return new Promise(function (resolve, reject) {
    fileStream.once('error', reject);
    s3.upload({
      Bucket: bucketName,
      Key: keyName,
      Body: fileStream,
      ContentType: 'text/html',
      ACL: 'public-read'
    }).promise().then((data) => { resolve(data) }, reject);
  });
}

function putObject_to_s3(bucketName, keyPrefix, filePath) {
  let htmlfile = fs.readFileSync(filePath, { encoding: 'utf8', flag: 'r' });
  return new Promise(function (resolve, reject) {
    s3.upload({
      Bucket: bucketName,
      Key: keyPrefix,
      Body: htmlfile,
      ContentType: 'text/html',
      ACL: 'public-read'
    }).promise().then((data) => { resolve(data) }, reject);
  });
}

function create_resume_page(dataContent, nameFile, event) {
  let header = '<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css"> ';
  let subtitle = '<h3>Files created via function lambda</h3>';
  let URL_base = `https://${event.buket_out}.s3.amazonaws.com/`
  if (event && event.hasOwnProperty("invokeby")) {
    subtitle += `<p><em>Summary and check requested by:</em><strong> ${event.invokeby}</strong><br>`
    subtitle += `<em>Date of request:</em> ${getCurrentDate()}</p>`
  }
  let title = `<div class="w3-container w3-teal"><h1>${'List of Results Alucloud31'}</h1></div>`
  let list = '<div class="w3-container"><ul>' + subtitle
  dataContent.Contents.forEach(function (obj, index) {
    let url_object = URL_base + obj.Key
    let str = JSON.stringify(obj.Key)
    if (!str.includes(nameFile.split('.')[0]))
      list = list + `<li><strong><a href="${url_object}" target="_blank">${obj.Key} </a></strong> - ${obj.LastModified.toUTCString()}</li>`;
  })
  list = list + '</ul></div><p></p>'
  let footer = `<div class="w3-container w3-teal"><h5>Static Web Page with AWSS3</h5></div>`
  let body = title + list
  return '<!DOCTYPE html>'
    + '<html>' + header + '</head><body>' + body + footer + '</body></html>';
}

function create_file(path, content) {
  fs.writeFileSync(path, content, { encoding: 'utf8', flag: 'w' })
}

function getCurrentDate() {
  var dt = new Date();
  return `${(dt.getMonth() + 1).toString().padStart(2, '0')}/${dt.getDate().toString().padStart(2, '0')}/${dt.getFullYear().toString().padStart(4, '0')} ${dt.getHours().toString().padStart(2, '0')}:${dt.getMinutes().toString().padStart(2, '0')}:${dt.getSeconds().toString().padStart(2, '0')}`
}