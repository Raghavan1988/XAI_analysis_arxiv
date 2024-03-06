import json
import matplotlib.pyplot as plt
import operator
import sys
import gradio as gr

def load_documents(file_path):
    """Load documents from a file."""
    with open(file_path, 'r') as file:
        documents = [line for line in file]
    return documents

def tokenize_keywords(keywords):
    """Split keywords string into a list of cleaned keywords."""
    return [keyword.strip().lower() for keyword in keywords.split(",") if keyword.strip() and len(keyword.strip()) >= 3]

def count_keywords(document, keywords):
    """Count occurrences of keywords in a document."""
    return sum(keyword in document.lower() for keyword in keywords)

def analyze_documents(documents, K1, K2, K3):
    """Analyze documents to find matches with given keyword sets."""
    denom_ids, num_ids = set(), set()
    keywords1_dict, keywords2_dict, keywords3_dict = {}, {}, {}
    keyword1_keyword2_dict = {}

    for i, document in enumerate(documents):
        content = document.lower()
        if any(keyword in content for keyword in K1):
            update_keyword_dicts(document, i, K1, K2, K3, denom_ids, num_ids, keywords1_dict, keywords2_dict, keywords3_dict, keyword1_keyword2_dict)

    return denom_ids, num_ids, keywords1_dict, keywords2_dict, keywords3_dict, keyword1_keyword2_dict

def update_keyword_dicts(document, i, K1, K2, K3, denom_ids, num_ids, k1_dict, k2_dict, k3_dict, k1_k2_dict):
    """Update dictionaries and sets based on document analysis."""
    content = document.lower()
    for keyword in K1:
        if keyword in content:
            k1_dict[keyword] = k1_dict.get(keyword, 0) + 1
            denom_ids.add(i)
            update_for_keyword_pairs(content, i, K2, num_ids, k2_dict, keyword, k1_k2_dict)
            update_for_keyword3(content, K3, k3_dict)

def update_for_keyword_pairs(content, i, K2, num_ids, k2_dict, keyword1, k1_k2_dict):
    """Update data structures for keyword pairs."""
    for k2 in K2:
        if k2 in content:
            k2_dict[k2] = k2_dict.get(k2, 0) + 1
            k1_k2_dict[keyword1 + "_" + k2] = k1_k2_dict.get(keyword1 + "_" + k2, 0) + 1
            num_ids.add(i)
            break

def update_for_keyword3(content, K3, k3_dict):
    """Update keyword3 dictionary."""
    for k3 in K3:
        if k3 in content:
            k3_dict[k3] = k3_dict.get(k3, 0) + 1

def generate_year_over_year_plot(documents, num_ids, term):
    """Generate and save a year-over-year plot."""
    years = aggregate_documents_by_year(documents, num_ids)
    plot_data_and_save(years, term)
    return years

def aggregate_documents_by_year(documents, num_ids):
    """Aggregate documents by year."""
    years = {}
    for i in num_ids:
        document = json.loads(documents[i])
        year = document['versions'][0]['created'].split()[3]
        if int(year) >= 2007:
            years.setdefault(year, []).append(i)
    return {year: years[year] for year in sorted(years)}

def plot_data_and_save(years, term):
    """Plot data and save the figure."""
    counts = [len(years[year]) for year in years]
    years_sorted = list(years.keys())

    plt.figure(figsize=(10, 6))
    plt.bar(years_sorted, counts, color='skyblue')
    plt.xlabel('Year')
    plt.ylabel('Number of Papers')
    plt.title(term.replace("_", " X ") + ' - Year-over-Year Paper Counts')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.savefig('year_over_year_plot' + term + '.png')

def generate_output_content(denom_ids, num_ids, years, term, k1_dict, k2_dict, k1_k2_dict):
    """Generate output content with statistics and links."""
    output_content = generate_summary(denom_ids, num_ids, term)
    output_content += generate_yearly_breakdown(years)
    output_content += generate_keyword_summary(k1_dict, "Keywords1")
    output_content += generate_keyword_summary(k2_dict, "Keywords2")
    output_content += generate_keyword_pairs_summary(k1_k2_dict)
    return output_content

def generate_summary(denom_ids, num_ids, term):
    """Generate a summary of the analysis."""
    ratio = (len(num_ids) * 100.0) / len(denom_ids) if denom_ids else 0
    summary = f"# Percentage of {term.split('_')[0]} that is {term.split('_')[1]}: {ratio:.2f}%\n"
    summary += "### Year over year results:\n"
    return summary

def generate_yearly_breakdown(years):
    """Generate a breakdown of results by year."""
    yearly_breakdown = ""
    for year, ids in years.items():
        yearly_breakdown += f"#### Papers in {year}: {len(ids)}\n"
        yearly_breakdown += ''.join(f"{json.loads(document)['title']}\n" for document in ids[:5])
    return yearly_breakdown

def generate_keyword_summary(keyword_dict, label):
    """Generate a summary of keyword occurrences."""
    summary = f"\n### Top {label}:\n"
    sorted_keywords = sorted(keyword_dict.items(), key=operator.itemgetter(1), reverse=True)
    for keyword, count in sorted_keywords:
        summary += f"- {keyword}: {count}\n"
    return summary

def generate_keyword_pairs_summary(k1_k2_dict):
    """Generate a summary for keyword pairs."""
    summary = "\n### Keyword Pairs:\n"
    for keyword_pair, count in k1_k2_dict.items():
        summary += f"- {keyword_pair.replace('_', ' and ')}: {count}\n"
    return summary

def get_overlap(documents, field1, field2, topic1, topic2):
    """Calculate the overlap between two sets of keywords across a document set."""
    K1, K2, K3 = tokenize_keywords(field1), tokenize_keywords(field2), []
    denom_ids, num_ids, k1_dict, k2_dict, k3_dict, k1_k2_dict = analyze_documents(documents, K1, K2, K3)
    term = f"{topic1}_{topic2}"
    years = generate_year_over_year_plot(documents, num_ids, term)
    output_content = generate_output_content(denom_ids, num_ids, years, term, k1_dict, k2_dict, k1_k2_dict)
    return output_content, 'year_over_year_plot'+ term +'.png'

def setup_gradio_interface():
    """Setup the Gradio interface for the application."""
    with gr.Blocks() as demo:
        gr.Markdown("<h1><center>Paper Trends</center></h1>")
        topic1 = gr.Textbox(label="Topic1")
        field1 = gr.Textbox(label="Keywords1", placeholder="Enter keywords for field1, comma separated")
        topic2 = gr.Textbox(label="Topic2")
        field2 = gr.Textbox(label="Keywords2", placeholder="Enter keywords for field2, comma separated")
        submit_btn = gr.Button("Submit")
        plot_output = gr.Image(label="Year-over-Year Plot")
        output_content = gr.Markdown(label="Output Content")
        submit_btn.click(get_overlap, [field1, field2, topic1, topic2], [output_content, plot_output])

    return demo

if __name__ == "__main__":
    documents = load_documents(sys.argv[1])
    demo = setup_gradio_interface()
    demo.launch(share=True)
