class State {
    constructor() {
      this.extractedText = '';
    }
  
    setExtractedText(text) {
      this.extractedText = text;
    }
  
    getExtractedText() {
      return this.extractedText;
    }
  }
  
  export const state = new State();