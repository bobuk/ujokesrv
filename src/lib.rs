use spin_sdk::http::{IntoResponse, Request, Response};
use spin_sdk::http_component;
use serde::{Deserialize, Serialize};
use serde_json;
use serde_json::json;
use walkdir::WalkDir;
use std::fs;
use std::path::Path;
use http::{Uri};
use anyhow::{Result, Ok};
use rand::seq::SliceRandom;
use std::collections::HashMap;

#[derive(Serialize, Deserialize, Debug)]
struct Joke {
    text: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct JokesFile {
    category: String,
    author: Option<String>,
    jokes: Vec<Joke>,
}

fn read_jokes_from_directory<P: AsRef<Path>>(path: P) -> Result<Vec<JokesFile>> {
    let mut jokes_files = Vec::new();

    for entry in WalkDir::new(path).into_iter().filter_map(|e| e.ok()) {
        if entry.path().extension().unwrap_or_default() == "json" {
            let file_content = fs::read_to_string(entry.path())?;
            let jokes_file: JokesFile = serde_json::from_str(&file_content)?;
            jokes_files.push(jokes_file);
        }
    }

    Ok(jokes_files)
}

fn get_path_from_req(req: Request) -> String {
    let url = req.uri().parse::<Uri>().unwrap();
    let uri_path = url.path();
    return uri_path[1..].to_string();
}

fn handle_joke_request(path: &str, jokesmap: &HashMap<String, &JokesFile>) -> Result<Response> {
    let mut randomng = rand::thread_rng();
    let jokesfile = jokesmap.get(path).unwrap();
    let joke = &jokesfile.jokes.choose(&mut randomng).unwrap();
    let response_body = json!({"category": path, "content": joke.text}).to_string();

    Ok(Response::builder()
        .status(200)
        .header("content-type", "application/json; charset=utf-8")
        .body(response_body).build())

}
/// A simple Spin HTTP component.
#[http_component]
fn handle_jokesrv_rust(req: Request) -> Result<impl IntoResponse> {
    let jokes = read_jokes_from_directory("jokes/")?;
    let mut categories: Vec<String> = Vec::new();
    let mut jokesmap: HashMap<String, &JokesFile> = HashMap::new();
    for jokefile in &jokes {
        categories.push(jokefile.category.clone());
        jokesmap.insert(jokefile.category.clone(), jokefile);
    }
    let path = get_path_from_req(req);
    if path == String::from("categories") {
        let json = serde_json::to_string(&categories).unwrap();
        return Ok(
            Response::builder()
                .status(200)
                .header("content-type", "application/json; charset=utf-8")
                .body(json).build())
    } else {
        if categories.contains(&path) {
            return handle_joke_request(&path, &jokesmap)
        }
    }
    handle_joke_request("oneliner", &jokesmap)
}
