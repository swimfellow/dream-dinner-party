# Dream Dinner Party
This repo exists to facilitate organization of code for the Dream Dinner Party project.

Running this application locally requires Python >=3.13.0 and dependencies suggested from each python script. To run locally, simply run:
```
python scripts/generate_responses.py
flask run
```
Navigate to http://localhost:5000/swimfellow. Once done, terminate the flask app and run:
```
python scripts/analysis.py
```

Roadmap of development:
- [x] Create choice interface
- [x] Test
    - [x] Pull ~~1000~~500 people from Wikidata
    - [x] Choose!
- [x] **APRIL 25** - v~~1.0~~Beta.1
- [x] **APRIL 25** - Launch presentation
- [x] **APRIL 26** - Present!
- [ ] Pending funding
    - [ ] Create code to generate (better) best characteristics
    - [ ] Create code to suggest more people
    - [ ] Convert to web backend
